# 🐍 Python Project Template

Template [Copier](https://copier.readthedocs.io/) pour bootstrapper un projet Python moderne.

## Utilisation

### Option 1 : Copier (recommandé)

```bash
# Installer copier
pip install copier

# Créer un nouveau projet
copier copy gh:YOUR_USERNAME/python-template mon-projet

# Mettre à jour un projet existant avec les dernières modifs du template
copier update
```

### Option 2 : GitHub "Use this template"

1. Cliquer sur **"Use this template"** → **"Create a new repository"**
2. Cloner le nouveau repo
3. Lancer le script d'initialisation :

```bash
cd mon-nouveau-repo
python scripts/init_project.py
```

Le script vous pose les mêmes questions que Copier et configure le projet.

## Ce que le template inclut

| Outil | Description |
|-------|-------------|
| **uv** ou **Poetry** | Gestion des dépendances (au choix) |
| **ruff** | Linter + formatter |
| **mypy** | Type checking |
| **pytest** + **coverage** | Tests unitaires et intégration |
| **pre-commit** | Hooks automatiques (optionnel) |
| **GitHub Actions** | CI/CD (optionnel) |
| **Docker** | Containerisation multi-stage (optionnel) |
| **MkDocs** | Documentation (optionnel) |

## Structure générée

```
mon-projet/
├── src/
│   └── mon_projet/
│       ├── __init__.py
│       └── __main__.py
├── tests/
│   ├── conftest.py
│   ├── ut/
│   └── it/
├── pyproject.toml
├── Makefile
├── Dockerfile          # si use_docker
├── .pre-commit-config.yaml  # si use_pre_commit
├── .github/workflows/ci.yml # si use_github_actions
└── README.md
```

## Personnalisation

Après génération, le projet est entièrement autonome. Modifiez ce que vous voulez.
Pour recevoir les mises à jour du template : `copier update`.

## Licence

MIT
