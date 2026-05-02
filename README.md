# 🐍 Python Project Template

> Modern, batteries-included [Copier](https://copier.readthedocs.io/) template for Python libraries and applications.

[![CI](https://github.com/rlhoussaine/python-template/actions/workflows/ci-template.yml/badge.svg)](https://github.com/rlhoussaine/python-template/actions/workflows/ci-template.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Copier](https://img.shields.io/github/v/release/copier-org/copier?label=Copier)](https://github.com/copier-org/copier/releases)
[![Minimum Copier](https://img.shields.io/badge/Copier-≥9.4-success)](https://copier.readthedocs.io/)

Template CI also runs security checks (including `pip-audit` on a generated project). There is no separate per-job badge URL for GitHub Actions; use the workflow run page for job-level status.

## Why this template?

- **uv-first** — Fast installs, lockfiles, and a single toolchain for develop, test, and CI.
- **CI-hardened** — Matrix generation checks, workflow linting, Docker build checks, timeouts, and least-privilege permissions on generated workflows.
- **AI-ready** — Ships `AGENTS.md` so assistants (Cursor, Copilot, Claude, and similar) follow your stack and conventions consistently.
- **Production-minded** — Optional multi-stage Docker (prod image without dev tooling, non-root), Renovate for dependency bumps, and opt-in PyPI Trusted Publishing (OIDC).

## Quick start

### With Copier (recommended)

```bash
pip install "copier>=9.4"
copier copy gh:rlhoussaine/python-template my-project
cd my-project
```

Answer the prompts (or use `--defaults` and override with `--data key=value`). Then install and run tests:

```bash
uv sync --all-groups
uv run pytest
```

### With GitHub “Use this template”

1. Click **Use this template** → **Create a new repository**.
2. Clone your new repository.
3. Run:

```bash
cd my-new-repo
python scripts/init_project.py
```

Initialization is interactive and mirrors the Copier questions.

## What’s included

| Component | Description | Default |
|-----------|-------------|---------|
| **uv** | Dependencies, environments, and lockfile | ✅ |
| **Ruff** | Lint + format | ✅ |
| **ty** | Type checking | ✅ |
| **deptry** | Unused/missing dependency checks | ✅ |
| **pip-audit** | Dependency security audit (also in CI hooks) | ✅ |
| **pytest** + **coverage** | Unit and integration layout | ✅ |
| **Just** | Cross-platform task runner with self-documented recipes | ✅ (`task_runner=just`) |
| **Make** | Alternative tasks via `Makefile` | opt-in (`make` / `both`) |
| **pre-commit** | Hooks (Ruff, ty, gitleaks, actionlint, etc.) | ✅ |
| **GitHub Actions** | CI, release-please, optional Publish, Scorecard, CodeQL, Dependabot | ✅ |
| **Docker** | Multi-stage `Dockerfile` | ✅ |
| **MkDocs** | Documentation site | opt-in |
| **data/ + Git LFS** | Version large datasets (CSV, Parquet, models, etc.) without bloating Git history; install `git lfs` locally | opt-in |
| **notebooks/** | Exploration notebooks | opt-in |
| **Hypothesis** | Property-based tests | opt-in |
| **Testcontainers** | Integration tests with real services in Docker | opt-in |
| **PyPI Trusted Publishing** | OIDC publish workflow — no long-lived API tokens | opt-in |
| **`.renovaterc.json`** | Renovate config for bumping `uv`/base images (included with Docker) | with Docker |
| **`AGENTS.md`** | Instructions for AI tools: layout, `uv run`, Conventional Commits, task runner | ✅ |

## Generated project structure

```
my-project/
├── AGENTS.md              # Conventions for AI assistants on this repo
├── src/
│   └── my_project/
│       ├── __init__.py
│       └── __main__.py
├── tests/
│   ├── conftest.py
│   ├── ut/
│   └── it/
├── data/                       # if use_data (Git LFS; install git-lfs)
├── notebooks/                  # if use_notebooks
├── pyproject.toml
├── justfile                    # if task_runner=just (default) or both
├── Makefile                    # if task_runner=make or both
├── Dockerfile                  # if use_docker; commit uv.lock for reproducible builds
├── .renovaterc.json            # if use_docker
├── .pre-commit-config.yaml     # if use_pre_commit
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              # if use_github_actions
│   │   ├── release.yml         # if use_github_actions
│   │   ├── publish.yml         # if use_pypi_publish
│   │   ├── scorecard.yml       # if use_github_actions
│   │   └── codeql.yml          # if use_github_actions
│   ├── dependabot.yml          # if use_github_actions
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
├── .gitattributes              # if use_data
├── CHANGELOG.md
├── LICENSE
└── README.md
```

If `use_github_actions` is false, the `.github/` folder and related security automation are omitted from the generated project.

## Updating an existing project

If the project was created with `copier copy`, refresh it from a newer template revision from the project root:

```bash
copier update
```

Resolve conflicts if any, re-run your test suite, and commit. Copier preserves answers in `.copier-answers.yml`. For details, see [`copier update` in the Copier docs](https://copier.readthedocs.io/en/stable/updating/).

Projects created only via `scripts/init_project.py` (template button) are not Copier-linked unless you adopt Copier afterward.

## Customization

After generation, the repo is yours: change tooling, layout, or CI as needed. To keep receiving template updates, prefer generating with `copier copy` and using `copier update`.

<details>
<summary><strong>What’s new in v0.2.0</strong></summary>

- **Just is now the default task runner** (cross-platform, auto-documented). Make remains available via `task_runner=make`.
- **PyPI Trusted Publishing (OIDC)** available with `use_pypi_publish=true` — no API tokens to rotate.
- **OpenSSF Scorecard, CodeQL, and Dependabot** ship with `use_github_actions=true`.
- **CI hardening** on generated workflows — concurrency groups, timeouts, least-privilege permissions per job.
- **Reproducible Docker** — pinned tooling, BuildKit cache mounts, production image without the `uv` binary, non-root user.
- **Modernized pre-commit** — gitleaks, actionlint, detect-private-key, mixed-line-ending.
- **Richer `pyproject.toml`** — project URLs, PyPI classifiers, extended Ruff rules, coverage `fail_under=80`.

</details>

### Docker and `uv.lock`

If you enable Docker, generate and commit `uv.lock` before the first production build:

```bash
uv sync
git add uv.lock && git commit -m "chore: add lockfile"
docker build -t my-project:latest --target prod .
```

## Contributing

Issues and pull requests are welcome. To work on the template locally:

1. Clone this repository.
2. Install Copier and uv; run the template CI workflow steps, or generate a scratch project with `copier copy . /tmp/example --trust` and run `uv sync && uv run pytest` inside it.

## License

MIT
