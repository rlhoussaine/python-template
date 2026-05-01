# 🐍 Python Project Template

Template [Copier](https://copier.readthedocs.io/) to bootstrap a modern Python project.

![CI Template](https://github.com/rlhoussaine/python-template/actions/workflows/ci-template.yml/badge.svg)
![Security](https://github.com/rlhoussaine/python-template/actions/workflows/ci-template.yml/badge.svg?job=security)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Copier](https://img.shields.io/badge/copier-9.0%2B-green.svg)

## Utilisation

### Option 1: Copier (recommended)

```bash
# Install copier
pip install copier

# Create a new project
copier copy gh:rlhoussaine/python-template my-project

# Update an existing project with latest template changes
copier update
```

### Option 2: GitHub "Use this template"

1. Click **"Use this template"** -> **"Create a new repository"**
2. Clone your new repository
3. Run the initializer script:

```bash
cd my-new-repo
python scripts/init_project.py
```

The script asks the same questions as Copier and configures the project.

## What the template includes

| Outil | Description |
|-------|-------------|
| **uv** | Dependency management |
| **ruff** | Linter + formatter |
| **ty** | Type checking |
| **deptry** | Dependency hygiene checks |
| **pip-audit** | Security audit of dependencies |
| **pytest** + **coverage** | Unit and integration tests |
| **pre-commit** | Automated hooks (optional) |
| **GitHub Actions** | CI/CD (optional) |
| **Docker** | Multi-stage containerization (optional) |
| **MkDocs** | Documentation (optional) |
| **data/ + Git LFS** | Data folder with LFS tracking (optional) |
| **notebooks/** | Exploration notebooks folder (optional) |

## Generated structure

```
my-project/
├── AGENTS.md              # directives pour assistants IA sur ce dépôt
├── src/
│   └── my_project/
│       ├── __init__.py
│       └── __main__.py
├── tests/
│   ├── conftest.py
│   ├── ut/
│   └── it/
├── data/                       # si use_data (Git LFS)
├── notebooks/                  # si use_notebooks
├── pyproject.toml
├── Makefile
├── Dockerfile                  # si use_docker ; requiert un `uv.lock` versionné pour un build reproductible
├── .pre-commit-config.yaml      # si use_pre_commit
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              # si use_github_actions
│   │   └── release.yml          # si use_github_actions (release-please)
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   └── feature_request.yml
│   └── pull_request_template.md
├── .gitattributes              # si use_data
├── CHANGELOG.md
├── LICENSE
└── README.md
```

💡 **Note sur la reproductibilité :** Le template génère un `pyproject.toml`. Pour garantir des builds Docker 100% reproductibles, vous **devez** générer le fichier `uv.lock` localement (en lançant `uv sync` ou `uv lock`) et le commiter sur Git avant de lancer un `docker build`.

Without the GitHub Actions option, the `.github/` folder is not included in the generated project.

## Customization

After generation, your project is fully autonomous. Customize anything you want.
To receive template updates later: `copier update`.

## License

MIT
