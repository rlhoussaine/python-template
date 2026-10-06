"""Render every combination of options and validate the generated files statically."""

from __future__ import annotations

import itertools
import json
import re
import subprocess
import tomllib
from typing import Any

import pytest
import yaml

from conftest import Generate

BOOL_OPTIONS = ("use_docker", "use_cli", "use_docs", "use_data", "use_notebooks")


def _combinations() -> list[Any]:
    params = []
    for provider in ("github", "gitlab", "none"):
        publish_values = (False,) if provider == "none" else (False, True)
        for publish in publish_values:
            for values in itertools.product((False, True), repeat=len(BOOL_OPTIONS)):
                data = dict(zip(BOOL_OPTIONS, values, strict=True))
                data["ci_provider"] = provider
                if provider != "none":
                    data["publish_package"] = publish
                enabled = [k.removeprefix("use_") for k, v in data.items() if v is True]
                params.append(pytest.param(data, id="-".join([provider, *enabled])))
    return params


# Leftover Jinja markers (GitHub's `${{ }}` expressions are legitimate).
JINJA_LEFTOVER = re.compile(r"(?<!\$)\{\{|\{%|%\}")


@pytest.mark.parametrize("data", _combinations())
def test_every_combination_renders_valid_files(generate: Generate, data: dict[str, Any]) -> None:
    project = generate(**data)
    files = [p for p in project.rglob("*") if p.is_file() and ".git" not in p.parts]

    for path in files:
        text = path.read_text(encoding="utf-8")
        # `{{args}}` is Just's own interpolation syntax.
        unrendered = text.replace("{{args}}", "") if path.name == "justfile" else text
        assert not JINJA_LEFTOVER.search(unrendered), f"unrendered Jinja in {path.name}"
        if path.suffix in {".yml", ".yaml"}:
            yaml.safe_load(text)
        elif path.suffix == ".toml":
            tomllib.loads(text)
        elif path.suffix == ".json":
            json.loads(text)

    # Optional pieces are present exactly when requested.
    expected = {
        "Dockerfile": data["use_docker"],
        ".dockerignore": data["use_docker"],
        "src/test_project/cli.py": data["use_cli"],
        "tests/ut/test_cli.py": data["use_cli"],
        "mkdocs.yml": data["use_docs"],
        ".gitattributes": data["use_data"],
        "data/.gitkeep": data["use_data"],
        "notebooks/.gitkeep": data["use_notebooks"],
        ".github/workflows/ci.yml": data["ci_provider"] == "github",
        ".gitlab-ci.yml": data["ci_provider"] == "gitlab",
        "renovate.json": data["ci_provider"] == "gitlab",
    }
    for rel, present in expected.items():
        assert (project / rel).exists() is present, rel

    if data["ci_provider"] == "github":
        workflows = sorted(str(p) for p in (project / ".github/workflows").glob("*.yml"))
        subprocess.run(["actionlint", *workflows], check=True, capture_output=True)
    elif data["ci_provider"] == "gitlab":
        subprocess.run(
            ["check-jsonschema", "--builtin-schema", "vendor.gitlab-ci", ".gitlab-ci.yml"],
            cwd=project,
            check=True,
            capture_output=True,
        )
