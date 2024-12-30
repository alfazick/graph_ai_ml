# Minimal Setup Guide for ArXiv Analysis Project

## Prerequisites

1. Python 3.10 or higher
2. Poetry (Python package manager)

## Installation Steps

1. Clone the repository:
```bash
git clone [your-repository-url]
cd arxiv-analysis
```

2. Install Poetry if you haven't already:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Configure Poetry to create virtual environment in the project directory (optional):
```bash
poetry config virtualenvs.in-project true
```

4. Install project dependencies:
```bash
poetry install
```

5. Activate the virtual environment:
```bash
poetry shell
```

## Project Structure

The project uses Poetry for dependency management with the following key dependencies:
- matplotlib (^3.7.1)
- networkx (^3.1)
- numpy (^1.24.0)
- pandas (^2.0.0)
- spacy (^3.6.0)
- py2neo (^2021.2.3)
- umap-learn (^0.5.3)
- hdbscan (^0.8.29)

## Common Issues

1. Python Version Mismatch:
   If you see a Python version error, make sure your Python version matches the one specified in `pyproject.toml`. You can modify the Python version requirement in `pyproject.toml` if needed.

2. Poetry not found in PATH:
   If you get a "poetry: command not found" error, you may need to add Poetry to your PATH:
   ```bash
   export PATH="/home/$USER/.local/bin:$PATH"
   ```

## Getting Started

After installation, you can start using the project within the Poetry virtual environment. Make sure to activate the environment using `poetry shell` before running any project commands.
