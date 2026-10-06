# 🐍 Python Project Template

> Opinionated, uv-first [Copier](https://copier.readthedocs.io/) template for Python libraries and applications — built for critical processing chains.

[![CI](https://github.com/rlhoussaine/python-template/actions/workflows/ci-template.yml/badge.svg)](https://github.com/rlhoussaine/python-template/actions/workflows/ci-template.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Minimum Copier](https://img.shields.io/badge/Copier-≥9.6-success)](https://copier.readthedocs.io/)

## Why this template?

- **Green at t0** — every generated project passes its own `just check` and `just test` (100 % coverage of the skeleton, branch coverage, coverage gate at 80 %) right after `copier copy`. The template CI proves it for every option combination.
- **One toolchain** — uv for everything (Python pinned in `.python-version`, uv in `[tool.uv] required-version`), Ruff, ty, deptry, pip-audit. Pre-commit hooks run the *locked* tools through `uv run`.
- **GitHub or GitLab** — first-class CI for both forges (self-hosted GitLab included), or none at all.
- **Release-ready** — CycloneDX SBOM and build artefacts on every release; PyPI Trusted Publishing (GitHub) or the project Package Registry (GitLab).
- **Production-minded Docker** — multi-stage, non-editable install: the prod image ships only the virtualenv, without uv nor sources, as a non-root user.
- **AI-ready** — `AGENTS.md` keeps assistants aligned with the stack and conventions.

## Quick start

```bash
uvx copier copy --trust gh:rlhoussaine/python-template my-project
cd my-project
just install   # uv sync --all-groups + git hooks
just check     # format, lint, types, dependencies
just test      # tests + coverage gate
```

`--trust` lets Copier run the post-generation tasks: `git init` and `uv lock`,
so the project is immediately installable with `uv sync --locked`. Answer the
prompts, or use `--defaults --data key=value` for a non-interactive run.

> **“Use this template” on GitHub is not supported**: a project created that way
> has no Copier answers and cannot be updated. Always generate with
> `uvx copier copy`.

## Questions

| Question | Values | Default |
|----------|--------|---------|
| `project_name`, `project_slug`, `project_description`, `author`, `email` | free text | — |
| `ci_provider` | `github`, `gitlab`, `none` | `github` |
| `repository_host` | e.g. `gitlab.my-company.fr` | `github.com` / `gitlab.com` |
| `repository_namespace` | user or group | `your-username` |
| `python_version` (minimum) | `3.11` … `3.14` | `3.12` |
| `license` | `MIT`, `Apache-2.0`, `GPL-3.0`, `Proprietary` | `MIT` |
| `use_docker` | multi-stage `Dockerfile` | ✅ |
| `use_cli` | click CLI (runtime dependency, `[project.scripts]`) | ❌ |
| `use_docs` | MkDocs Material + mkdocstrings | ❌ |
| `use_data` | `data/` tracked with Git LFS | ❌ |
| `use_notebooks` | `notebooks/` folder | ❌ |
| `publish_package` | publish on release (asked when `ci_provider != none`) | ❌ |

## What’s included

| Component | Details |
|-----------|---------|
| **uv** | Dependencies, lockfile, Python version (`.python-version`), `required-version` |
| **Ruff** | Format + rich rule set (bandit, bugbear, pydocstyle Google, `T20` no-print, logging rules…) |
| **ty** | Type checking, warnings are errors |
| **deptry** | Missing / unused / misplaced dependencies |
| **pip-audit** | Audit of the locked environment (CI, `just audit`, pre-push hook) |
| **pytest** | `--strict-markers`, `--strict-config`, `xfail_strict`, `filterwarnings = ["error"]`, branch coverage, Hypothesis |
| **Logging** | `logging_config.configure_logging()`: ISO 8601 UTC timestamps on stderr, idempotent |
| **Just** | Single task runner (`just --list`) |
| **pre-commit** | Hygiene, gitleaks, actionlint / GitLab CI schema, and local `uv run` hooks (ruff, ty, `uv lock --check`, pip-audit on pre-push, commitizen on commit-msg) |
| **GitHub** | CI (matrix derived from the minimum Python), release-please → build + SBOM + provenance attestation (+ PyPI), CodeQL, Scorecard, Dependabot (uv, actions, docker); actions pinned by SHA |
| **GitLab** | CI (quality, Code Quality report, tests matrix with JUnit + Cobertura, docs/Pages), tag pipeline → build + SBOM + Package Registry + release, Renovate, MR/issue templates |
| **Releases** | Conventional Commits; release-please (GitHub) or `just bump` with commitizen (GitLab / none) — both keep `uv.lock` in sync |
| **Docker** | `uv sync --locked --no-editable`; prod image = `.venv` only, no uv, non-root |
| **`AGENTS.md`** | Conventions for AI assistants |

## Generated project structure

```
my-project/
├── src/my_project/
│   ├── __init__.py          # __version__ read from the installed metadata
│   ├── __main__.py
│   ├── cli.py               # if use_cli
│   ├── logging_config.py
│   └── py.typed
├── tests/
│   ├── conftest.py
│   ├── ut/                  # unit tests (100 % of the skeleton)
│   └── it/                  # integration tests (runs `python -m my_project`)
├── data/                    # if use_data (Git LFS, scoped to data/**)
├── notebooks/               # if use_notebooks
├── docs/ + mkdocs.yml       # if use_docs
├── .github/                 # if ci_provider=github
├── .gitlab/ + .gitlab-ci.yml + renovate.json   # if ci_provider=gitlab
├── release-please-config.json + .release-please-manifest.json  # if github
├── Dockerfile + .dockerignore                  # if use_docker
├── .copier-answers.yml      # enables `copier update`
├── .pre-commit-config.yaml
├── .python-version
├── AGENTS.md
├── CHANGELOG.md
├── justfile
├── pyproject.toml
└── uv.lock                  # created by the post-generation task
```

## Updating an existing project

```bash
uvx copier update --trust
```

Copier reads `.copier-answers.yml`, re-applies the template diff, then re-runs
`uv lock`. Resolve conflicts if any, run `just check && just test`, and commit.
See [`copier update`](https://copier.readthedocs.io/en/stable/updating/).

<details>
<summary><strong>What’s new in v0.3.0 (breaking)</strong></summary>

- **Fixed**: ty configuration (`[tool.ty.environment]`), coverage gate green at t0,
  `click` is a runtime dependency, `.copier-answers.yml` is generated, publication
  is chained to release-please (a `GITHUB_TOKEN` release never triggers
  `on: release`), CI matrix derived from the minimum Python version.
- **Questions removed**: `task_runner` (Just only), `use_pre_commit` (always on),
  `use_hypothesis` (always on), `use_testcontainers`, `scripts/init_project.py`.
- **Questions renamed**: `use_github_actions` → `ci_provider` (`github` / `gitlab` / `none`),
  `github_username` → `repository_namespace` (+ `repository_host`),
  `use_pypi_publish` → `publish_package`.
- **Added**: GitLab CI, `.python-version`, `required-version`, Copier `_tasks`,
  strict pytest, logging module, CycloneDX SBOM, commitizen bump flow, template
  tests in pytest.
- **Changed**: single dependency bot per forge, Git LFS scoped to `data/`,
  single-source version, non-editable Docker install, `ENTRYPOINT` in the prod image.

</details>

## Contributing

The template is tested with pytest and Copier's Python API (`tests/`):

```bash
uv sync
uv run pytest -n auto                 # render all combinations + regressions + end-to-end
uv run pytest -m "not e2e" -n auto    # fast: rendering and static checks only
uv run pytest -m docker               # build the generated Dockerfile (needs Docker)
```

- `test_render.py` renders **every** option combination and validates YAML / TOML /
  JSON, actionlint (GitHub) and the GitLab CI schema.
- `test_regressions.py` holds one test per known defect.
- `test_e2e.py` generates projects (with `_tasks`), then runs `uv sync --locked`,
  `just check`, `just test`, `just build`, `copier update` and `cz bump`, on every
  supported Python version.

## License

MIT
