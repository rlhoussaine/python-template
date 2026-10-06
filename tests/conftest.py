"""Fixtures to render the template with Copier's Python API."""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from copier import run_copy

ROOT = Path(__file__).resolve().parents[1]
PYTHON_VERSIONS = ["3.11", "3.12", "3.13", "3.14"]
DEFAULT_DATA: dict[str, Any] = {
    "project_name": "Test Project",
    "author": "CI Bot",
    "email": "ci@example.com",
    "repository_namespace": "ci-bot",
}

Generate = Callable[..., Path]

_LEAKY_ENV = frozenset({"VIRTUAL_ENV", "UV_PYTHON", "UV_PROJECT_ENVIRONMENT"})


def git(cwd: Path, *args: str) -> str:
    """Run git with a fixed identity, return stdout."""
    return subprocess.run(
        ["git", "-c", "user.name=CI", "-c", "user.email=ci@example.com", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def run(cwd: Path, *cmd: str, timeout: int = 900) -> subprocess.CompletedProcess[str]:
    """Run a command in a generated project and fail with its output on error."""
    # Isolate the generated project from this repository's environment
    # (`uv run`, or setup-uv which exports UV_PYTHON in CI).
    env = {k: v for k, v in os.environ.items() if k not in _LEAKY_ENV}
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env, timeout=timeout)
    assert result.returncode == 0, (
        f"`{' '.join(cmd)}` failed ({result.returncode}) in {cwd}\n"
        f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )
    return result


@pytest.fixture(scope="session")
def template_repo(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Snapshot of the working tree committed in a throwaway git repository.

    Copier records the template commit in `.copier-answers.yml`; using a clean,
    committed snapshot makes `copier update` testable and includes local edits.
    """
    repo = tmp_path_factory.mktemp("template-repo")
    shutil.copy2(ROOT / "copier.yml", repo / "copier.yml")
    shutil.copytree(
        ROOT / "template",
        repo / "template",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    git(repo, "init", "--quiet", "--initial-branch=main")
    git(repo, "add", "--all")
    git(repo, "commit", "--quiet", "--message", "snapshot")
    return repo


@pytest.fixture
def generate(template_repo: Path, tmp_path: Path) -> Generate:
    """Render the template; `tasks=True` also runs `_tasks` (git init, uv lock)."""

    def _generate(*, tasks: bool = False, name: str = "project", **data: Any) -> Path:
        dst = tmp_path / name
        run_copy(
            str(template_repo),
            dst,
            data={**DEFAULT_DATA, **data},
            vcs_ref="HEAD",
            defaults=True,
            unsafe=True,
            quiet=True,
            skip_tasks=not tasks,
        )
        return dst

    return _generate
