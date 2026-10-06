"""Build the generated Dockerfile (run with `pytest -m docker`)."""

from __future__ import annotations

import uuid

import pytest

from conftest import Generate, run

pytestmark = pytest.mark.docker


@pytest.mark.parametrize("use_cli", [False, True])
def test_prod_image(generate: Generate, use_cli: bool) -> None:
    project = generate(tasks=True, use_docker=True, use_cli=use_cli)
    tag = f"template-test-{uuid.uuid4().hex[:12]}:prod"
    run(project, "docker", "build", "--target", "prod", "--tag", tag, ".")
    try:

        def sh(script: str) -> str:
            return run(
                project, "docker", "run", "--rm", "--entrypoint", "sh", tag, "-c", script
            ).stdout.strip()

        assert sh("command -v uv || echo absent") == "absent"
        assert sh("id -u") != "0"
        # Non-editable install: only the virtualenv is shipped, no sources.
        assert sh("ls -A /app") == ".venv"

        output = run(project, "docker", "run", "--rm", tag, *(["hello"] if use_cli else []))
        if use_cli:
            assert "Hello World, from Test Project!" in output.stdout
        else:
            assert "Hello from Test Project!" in output.stderr
    finally:
        run(project, "docker", "image", "rm", "--force", tag)
