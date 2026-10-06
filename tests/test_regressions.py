"""Regression tests: one per defect found in a freshly generated project."""

from __future__ import annotations

import json
import re
import subprocess
import tomllib
from pathlib import Path
from typing import Any

import pytest
import yaml

from conftest import PYTHON_VERSIONS, ROOT, Generate


def _toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


# ── Blocking bugs ────────────────────────────────────────────────────────────


def test_ty_python_version_lives_in_environment_table(generate: Generate) -> None:
    ty = _toml(generate(python_version="3.13") / "pyproject.toml")["tool"]["ty"]
    assert ty["environment"]["python-version"] == "3.13"
    assert "python-version" not in ty


@pytest.mark.parametrize("use_cli", [False, True])
def test_skeleton_ships_tests_for_every_module(generate: Generate, use_cli: bool) -> None:
    project = generate(use_cli=use_cli)
    tests = "\n".join(p.read_text() for p in (project / "tests").rglob("test_*.py"))
    assert "configure_logging" in tests
    assert "main()" in tests or "CliRunner" in tests
    if use_cli:
        assert "CliRunner" in tests


def test_cli_dependency_is_a_runtime_dependency(generate: Generate) -> None:
    pyproject = _toml(generate(use_cli=True) / "pyproject.toml")
    assert any(dep.startswith("click") for dep in pyproject["project"]["dependencies"])
    for group in pyproject["dependency-groups"].values():
        assert not any(dep.startswith("click") for dep in group)
    assert pyproject["project"]["scripts"] == {"test_project": "test_project.cli:main"}


def test_answers_file_enables_copier_update(generate: Generate) -> None:
    answers = _yaml(generate(use_cli=True) / ".copier-answers.yml")
    assert answers["_commit"]
    assert answers["_src_path"]
    assert answers["use_cli"] is True
    assert "python_versions" not in answers  # computed values are not stored


def test_publication_is_chained_to_release_please(generate: Generate) -> None:
    project = generate(publish_package=True)
    workflows = {p.name: _yaml(p) for p in (project / ".github/workflows").glob("*.yml")}

    # GITHUB_TOKEN-created releases never trigger `on: release` workflows.
    for name, wf in workflows.items():
        assert "release" not in wf[True], f"{name} relies on an `on: release` trigger"

    jobs = workflows["release.yml"]["jobs"]
    assert jobs["release-please"]["outputs"]["release_created"]
    assert jobs["build"]["needs"] == "release-please"
    assert jobs["build"]["if"] == "needs.release-please.outputs.release_created == 'true'"
    assert jobs["publish"]["needs"] == "build"
    assert jobs["publish"]["permissions"] == {"id-token": "write"}


def test_no_publish_job_unless_requested(generate: Generate) -> None:
    jobs = _yaml(generate() / ".github/workflows/release.yml")["jobs"]
    assert "publish" not in jobs
    assert "build" in jobs  # SBOM + provenance are produced for every release


@pytest.mark.parametrize("python_version", PYTHON_VERSIONS)
def test_ci_matrix_follows_minimum_python_version(generate: Generate, python_version: str) -> None:
    expected = [v for v in PYTHON_VERSIONS if v >= python_version]

    gh = generate(python_version=python_version, name="gh")
    ci = _yaml(gh / ".github/workflows/ci.yml")
    assert ci["jobs"]["test"]["strategy"]["matrix"]["python-version"] == expected

    gl = generate(python_version=python_version, ci_provider="gitlab", name="gl")
    matrix = _yaml(gl / ".gitlab-ci.yml")["test"]["parallel"]["matrix"]
    assert matrix == [{"PYTHON_VERSION": expected}]

    classifiers = _toml(gh / "pyproject.toml")["project"]["classifiers"]
    assert [c.rsplit(" ", 1)[1] for c in classifiers if re.search(r":: 3\.\d+$", c)] == expected


# ── Inconsistencies ──────────────────────────────────────────────────────────


def test_lfs_is_scoped_to_data_and_data_is_not_ignored(generate: Generate) -> None:
    project = generate(use_data=True)
    rules = [
        line
        for line in (project / ".gitattributes").read_text().splitlines()
        if line and not line.startswith("#")
    ]
    assert rules
    assert all(rule.startswith("data/**/") for rule in rules)
    for ext in ("tif", "jp2", "nc", "h5", "parquet"):
        assert f"data/**/*.{ext} filter=lfs diff=lfs merge=lfs -text" in rules
    assert "data" not in (project / ".gitignore").read_text()


def test_version_has_a_single_source(generate: Generate) -> None:
    project = generate()
    init = (project / "src/test_project/__init__.py").read_text()
    assert "importlib.metadata" in init
    assert not re.search(r"__version__\s*=\s*['\"]", init)


def test_pre_commit_python_hooks_use_the_locked_environment(generate: Generate) -> None:
    config = _yaml(generate() / ".pre-commit-config.yaml")
    local = next(r for r in config["repos"] if r["repo"] == "local")["hooks"]
    entries = {hook["id"]: hook["entry"] for hook in local}
    for hook_id in ("ruff-check", "ruff-format", "ty", "pip-audit", "commitizen"):
        assert entries[hook_id].startswith("uv run "), hook_id
    remote = {r["repo"] for r in config["repos"]}
    assert not {r for r in remote if "ruff" in r or "pip-audit" in r or "commitizen" in r}
    assert set(config["default_install_hook_types"]) == {"pre-commit", "commit-msg", "pre-push"}


@pytest.mark.parametrize(
    ("provider", "bot_files", "absent"),
    [
        ("github", [".github/dependabot.yml"], ["renovate.json", ".renovaterc.json"]),
        ("gitlab", ["renovate.json"], [".github", ".renovaterc.json"]),
        ("none", [], [".github", "renovate.json", ".renovaterc.json"]),
    ],
)
def test_single_dependency_bot_per_forge(
    generate: Generate, provider: str, bot_files: list[str], absent: list[str]
) -> None:
    project = generate(ci_provider=provider, use_docker=True)
    for rel in absent:
        assert not (project / rel).exists(), rel
    for rel in bot_files:
        schema = "vendor.dependabot" if rel.endswith("dependabot.yml") else "vendor.renovate"
        subprocess.run(
            ["check-jsonschema", "--builtin-schema", schema, rel], cwd=project, check=True
        )
    if provider == "github":
        ecosystems = {u["package-ecosystem"] for u in _yaml(project / bot_files[0])["updates"]}
        assert ecosystems == {"uv", "github-actions", "docker"}


def test_docker_prod_image_contains_only_the_virtualenv(generate: Generate) -> None:
    dockerfile = (generate(use_docker=True) / "Dockerfile").read_text()
    sync_lines = [line for line in dockerfile.splitlines() if "uv sync" in line]
    assert all("--locked" in line for line in sync_lines)
    assert all("--no-editable" in line for line in sync_lines if "--all-groups" not in line)
    prod = dockerfile.split("AS prod", 1)[1]
    assert [line for line in prod.splitlines() if line.startswith("COPY")] == [
        "COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv"
    ]


def test_github_ci_relies_on_setup_uv_only(generate: Generate) -> None:
    project = generate(use_docs=True)
    for path in (project / ".github/workflows").glob("*.yml"):
        text = path.read_text()
        assert "setup-python" not in text, path.name
        assert "uv lock --locked" not in text, path.name
        # Every third-party action is pinned to a full commit SHA.
        for ref in re.findall(r"uses: (\S+)", text):
            assert re.search(r"@[0-9a-f]{40}$", ref), f"{path.name}: {ref} is not pinned"
    ci = (project / ".github/workflows/ci.yml").read_text()
    assert ci.count("uv sync --locked --all-groups") == 2


def test_ruff_uses_current_rule_codes(generate: Generate) -> None:
    select = _toml(generate() / "pyproject.toml")["tool"]["ruff"]["lint"]["select"]
    assert "TC" in select
    assert "TCH" not in select


def test_toolchain_is_pinned(generate: Generate) -> None:
    project = generate(python_version="3.13")
    assert (project / ".python-version").read_text().strip() == "3.13"
    required = _toml(project / "pyproject.toml")["tool"]["uv"]["required-version"]
    assert required.startswith(">=")


def test_pytest_is_strict(generate: Generate) -> None:
    pyproject = _toml(generate() / "pyproject.toml")
    pytest_cfg = pyproject["tool"]["pytest"]["ini_options"]
    assert pytest_cfg["xfail_strict"] is True
    assert pytest_cfg["filterwarnings"] == ["error"]
    assert "--strict-markers" in pytest_cfg["addopts"]
    assert pyproject["tool"]["coverage"]["run"]["branch"] is True


def test_release_please_keeps_uv_lock_in_sync(generate: Generate) -> None:
    project = generate(project_name="My-Great Project")
    config = json.loads((project / "release-please-config.json").read_text())
    extra = config["packages"]["."]["extra-files"]
    assert extra == [
        {
            "type": "toml",
            "path": "uv.lock",
            "jsonpath": "$.package[?(@.name.value=='my-great-project')].version",
        }
    ]


# ── Template repository hygiene ──────────────────────────────────────────────


def test_template_ci_has_no_silenced_steps() -> None:
    for path in (ROOT / ".github/workflows").glob("*.yml"):
        text = path.read_text()
        assert "continue-on-error" not in text, path.name
        assert "|| true" not in text, path.name


def test_no_bytecode_is_tracked() -> None:
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.splitlines()
    assert not [f for f in tracked if f.endswith(".pyc") or "__pycache__" in f]
