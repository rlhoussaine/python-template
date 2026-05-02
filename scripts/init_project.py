#!/usr/bin/env python3
"""
Post-clone initializer for GitHub "Use this template" workflow.

Replicates what `copier copy` does: asks questions, renders Jinja templates,
renames directories, removes conditional files, and sets up the project.

Usage:
    cd my-new-repo
    python scripts/init_project.py
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

QUESTIONS = [
    ("project_name", "Nom du projet", None),
    ("project_slug", "Slug Python (snake_case)", None),
    ("project_description", "Description courte", "A Python project."),
    ("author", "Auteur", None),
    ("github_username", "Username GitHub", None),
    ("email", "Email", None),
    ("python_version", "Version Python minimale [3.11/3.12/3.13/3.14]", "3.12"),
    ("license", "Licence [MIT/Apache-2.0/GPL-3.0/Proprietary]", "MIT"),
    ("use_docker", "Inclure Dockerfile ? [y/n]", "y"),
    ("use_github_actions", "Inclure CI GitHub Actions ? [y/n]", "y"),
    ("use_pre_commit", "Inclure pre-commit ? [y/n]", "y"),
    ("use_docs", "Inclure MkDocs ? [y/n]", "n"),
    ("use_cli", "Inclure un CLI click ? [y/n]", "n"),
    ("use_data", "Inclure un dossier data/ avec Git LFS ? [y/n]", "n"),
    ("use_notebooks", "Inclure un dossier notebooks/ ? [y/n]", "n"),
    ("use_hypothesis", "Inclure Hypothesis (property-based testing) ? [y/n]", "n"),
    ("use_testcontainers", "Inclure Testcontainers ? [y/n]", "n"),
    ("task_runner", "Orchestrateur de tâches [just/make/both]", "just"),
    ("use_pypi_publish", "Publication PyPI via OIDC ? [y/n]", "n"),
]


def ask(key, prompt, default):
    suffix = f" [{default}]" if default else ""
    while True:
        value = input(f"  {prompt}{suffix}: ").strip()
        if not value and default:
            return default
        if value:
            return value
        print("    Valeur requise.")


def to_bool(val):
    return val.lower() in ("y", "yes", "true", "1", "oui")


def slugify(name):
    return re.sub(r"[^a-z0-9_]", "", name.lower().replace(" ", "_").replace("-", "_"))


def collect_answers():
    print("\n Python Project Initializer\n")
    answers = {}
    for key, prompt, default in QUESTIONS:
        if key == "project_slug":
            derived = slugify(answers["project_name"])
            answers[key] = ask(key, prompt, derived)
        else:
            answers[key] = ask(key, prompt, default)
    for k in (
        "use_docker",
        "use_github_actions",
        "use_pre_commit",
        "use_docs",
        "use_cli",
        "use_data",
        "use_notebooks",
        "use_hypothesis",
        "use_testcontainers",
        "use_pypi_publish",
    ):
        answers[k] = to_bool(answers[k])
    return answers


def render_string(text, ctx):
    """Render Jinja templates. Uses jinja2 if available, else basic substitution."""
    try:
        from jinja2 import Environment
        env = Environment(keep_trailing_newline=True)
        return env.from_string(text).render(**ctx)
    except ImportError:
        # Minimal fallback: supports simple {% if flag %}...{% endif %} blocks.
        if_pattern = re.compile(r"{%\s*if\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*%}(.*?){%\s*endif\s*%}")
        while True:
            new_text = if_pattern.sub(
                lambda m: m.group(2) if ctx.get(m.group(1), False) else "",
                text,
            )
            if new_text == text:
                break
            text = new_text
        for key, val in ctx.items():
            text = text.replace("{{ " + key + " }}", str(val))
            text = text.replace("{{" + key + "}}", str(val))
        return text


def render_tree(root, ctx):
    # 1) Render *.jinja file contents and strip .jinja suffix
    for path in sorted(root.rglob("*.jinja"), reverse=True):
        content = path.read_text(encoding="utf-8")
        rendered = render_string(content, ctx)
        target = path.with_suffix("")
        target.write_text(rendered, encoding="utf-8")
        path.unlink()

    # 2) Render conditional names like {% if ... %}name{% endif %} and rename/delete
    for path in sorted(root.rglob("*"), reverse=True):
        if "{%" not in path.name:
            continue
        rendered_name = render_string(path.name, ctx).strip()
        if not rendered_name:
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            else:
                path.unlink(missing_ok=True)
            continue

        target = path.with_name(rendered_name)
        if target != path and not target.exists():
            path.rename(target)

    # 3) Rename {{ project_slug }} directories
    for dirpath in sorted(root.rglob("{{ project_slug }}"), reverse=True):
        if dirpath.is_dir():
            new_name = dirpath.parent / ctx["project_slug"]
            if not new_name.exists():
                dirpath.rename(new_name)

    # 4) Keep explicit removals as a safety net
    if not ctx["use_docker"]:
        (root / "Dockerfile").unlink(missing_ok=True)
    if not ctx["use_pre_commit"]:
        (root / ".pre-commit-config.yaml").unlink(missing_ok=True)
    if not ctx["use_github_actions"]:
        ci = root / ".github" / "workflows" / "ci.yml"
        ci.unlink(missing_ok=True)
        release = root / ".github" / "workflows" / "release.yml"
        release.unlink(missing_ok=True)
        shutil.rmtree(root / ".github" / "ISSUE_TEMPLATE", ignore_errors=True)
        (root / ".github" / "pull_request_template.md").unlink(missing_ok=True)
    if not ctx["use_docs"]:
        shutil.rmtree(root / "docs", ignore_errors=True)
        (root / "mkdocs.yml").unlink(missing_ok=True)
    if not ctx["use_data"]:
        shutil.rmtree(root / "data", ignore_errors=True)
        (root / ".gitattributes").unlink(missing_ok=True)
    if not ctx["use_notebooks"]:
        shutil.rmtree(root / "notebooks", ignore_errors=True)

    if ctx["task_runner"] == "just":
        (root / "Makefile").unlink(missing_ok=True)
    elif ctx["task_runner"] == "make":
        (root / "justfile").unlink(missing_ok=True)

    if not ctx["use_pypi_publish"]:
        (root / ".github" / "workflows" / "publish.yml").unlink(missing_ok=True)

    if not ctx["use_github_actions"]:
        for wf in ("scorecard.yml", "codeql.yml"):
            (root / ".github" / "workflows" / wf).unlink(missing_ok=True)
        (root / ".github" / "dependabot.yml").unlink(missing_ok=True)


def run_cmd(cmd, cwd=None):
    try:
        subprocess.run(cmd, cwd=cwd, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"  Warning: {' '.join(cmd)} failed: {e}")


def post_init(root, ctx):
    # Clean template machinery
    shutil.rmtree(root / "template", ignore_errors=True)
    shutil.rmtree(root / "scripts", ignore_errors=True)
    (root / "copier.yml").unlink(missing_ok=True)

    # Overwrite the repo README with the rendered project README
    print("\n Installing dependencies...")
    run_cmd(["uv", "sync", "--all-groups"], cwd=root)

    if ctx["use_pre_commit"]:
        print(" Setting up pre-commit hooks...")
        run_cmd(["uv", "run", "pre-commit", "install", "--install-hooks"], cwd=root)

    print(f"\n Project '{ctx['project_name']}' ready!")
    print("   uv run pytest")


def main():
    root = Path.cwd()

    if not (root / "copier.yml").exists() and not (root / "template").exists():
        print("Run this script from the cloned template repo root.")
        sys.exit(1)

    ctx = collect_answers()

    # Copy template/ contents to root
    template_dir = root / "template"
    if template_dir.exists():
        for item in template_dir.iterdir():
            dest = root / item.name
            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)

    print("\n Rendering templates...")
    render_tree(root, ctx)
    post_init(root, ctx)


if __name__ == "__main__":
    main()
