# 🐍 Python Project Template

Template [Copier](https://copier.readthedocs.io/) to bootstrap a modern Python project.

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
| **uv** or **Poetry** | Dependency management (choose one) |
| **ruff** | Linter + formatter |
| **mypy** | Type checking |
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
├── src/
│   └── my_project/
│       ├── __init__.py
│       └── __main__.py
├── tests/
│   ├── conftest.py
│   ├── ut/
│   └── it/
├── data/                # if use_data (Git LFS)
├── notebooks/           # if use_notebooks
├── pyproject.toml
├── Makefile
├── Dockerfile          # si use_docker
├── .pre-commit-config.yaml  # si use_pre_commit
├── .github/workflows/ci.yml # si use_github_actions
├── .gitattributes      # if use_data
├── CHANGELOG.md
├── LICENSE
└── README.md
```

## Customization

After generation, your project is fully autonomous. Customize anything you want.
To receive template updates later: `copier update`.

## License

MIT
