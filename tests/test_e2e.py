"""End-to-end: a freshly generated project must be green with its own tooling.

Each test runs Copier's `_tasks` (git init + uv lock), installs the project with
`uv sync --locked`, then runs `just check` and `just test` (coverage gate
included) exactly as a developer or the generated CI would.
"""

from __future__ import annotations

import itertools
import sys
import tomllib
import zipfile
from pathlib import Path

import pytest
import yaml

from conftest import PYTHON_VERSIONS, Generate, git, run

pytestmark = pytest.mark.e2e


def _assert_green(project: Path) -> None:
    assert (project / ".git").is_dir(), "_tasks must initialise a git repository"
    assert (project / "uv.lock").is_file(), "_tasks must create uv.lock"
    run(project, "uv", "sync", "--locked", "--all-groups")
    run(project, "just", "check")
    result = run(project, "just", "test")
    assert "Required test coverage of 80" in result.stdout


# Options that change Python code or dependencies; the others (docker, data,
# notebooks) only add files, validated statically by test_render.py.
@pytest.mark.parametrize(
    ("provider", "use_cli", "use_docs"),
    list(itertools.product(("github", "gitlab", "none"), (False, True), (False, True))),
)
def test_generated_project_is_green(
    generate: Generate, provider: str, use_cli: bool, use_docs: bool
) -> None:
    project = generate(tasks=True, ci_provider=provider, use_cli=use_cli, use_docs=use_docs)
    _assert_green(project)
    if use_docs:
        run(project, "uv", "run", "mkdocs", "build", "--strict")


@pytest.mark.parametrize("python_version", PYTHON_VERSIONS)
def test_every_supported_python_version(generate: Generate, python_version: str) -> None:
    project = generate(tasks=True, python_version=python_version, use_cli=True)
    _assert_green(project)
    version = run(project, "uv", "run", "python", "--version").stdout
    assert version.startswith(f"Python {python_version}.")


@pytest.mark.parametrize("license_id", ["MIT", "Apache-2.0", "GPL-3.0", "Proprietary"])
def test_build_wheel_and_sbom(generate: Generate, license_id: str) -> None:
    project = generate(tasks=True, use_cli=True, license=license_id)
    run(project, "just", "build")

    wheel = next((project / "dist").glob("*.whl"))
    with zipfile.ZipFile(wheel) as zf:
        metadata = zf.read(next(n for n in zf.namelist() if n.endswith("METADATA"))).decode()
        assert "test_project/py.typed" in zf.namelist()
    assert "Requires-Dist: click" in metadata

    sbom = yaml.safe_load((project / "sbom.cdx.json").read_text())  # JSON is YAML
    assert sbom["bomFormat"] == "CycloneDX"
    assert "click" in {c["name"] for c in sbom["components"]}
    assert "pytest" not in {c["name"] for c in sbom["components"]}

    # The installed console script works outside the dev environment.
    out = run(project, "uv", "tool", "run", "--from", str(wheel), "test_project", "hello")
    assert "Hello World, from Test Project!" in out.stdout


def test_copier_update_applies_new_answers(generate: Generate) -> None:
    project = generate(tasks=True)
    git(project, "add", "--all")
    git(project, "commit", "--quiet", "--no-verify", "--message", "feat: initial commit")

    run(
        project,
        sys.executable,
        "-m",
        "copier",
        "update",
        "--trust",
        "--defaults",
        "--data",
        "use_cli=true",
    )

    pyproject = tomllib.loads((project / "pyproject.toml").read_text())
    assert any(dep.startswith("click") for dep in pyproject["project"]["dependencies"])
    assert (project / "src/test_project/cli.py").is_file()
    assert yaml.safe_load((project / ".copier-answers.yml").read_text())["use_cli"] is True
    _assert_green(project)


def test_commitizen_bump_keeps_lockfile_in_sync(generate: Generate) -> None:
    project = generate(tasks=True, ci_provider="gitlab")
    run(project, "uv", "sync", "--locked", "--all-groups")
    for key, value in {"user.name": "CI", "user.email": "ci@example.com"}.items():
        git(project, "config", key, value)
    git(project, "add", "--all")
    git(project, "commit", "--quiet", "--message", "feat: initial commit")

    run(project, "just", "bump", "--yes")

    assert "v0.2.0" in git(project, "tag").split()
    assert 'version = "0.2.0"' in (project / "pyproject.toml").read_text()
    run(project, "uv", "lock", "--check")
    assert "## v0.2.0" in (project / "CHANGELOG.md").read_text()
