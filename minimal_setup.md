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

## Setting up Neo4j

1. Download and extract Neo4j:
```bash
# Download Neo4j
wget https://dist.neo4j.org/neo4j-community-5.15.0-unix.tar.gz

# Extract Neo4j
tar -xf neo4j-community-5.15.0-unix.tar.gz
```

2. Configure Neo4j:
```bash
# Create neo4j.conf
cat > neo4j-community-5.15.0/conf/neo4j.conf << EOL
# Network Settings
server.default_listen_address=0.0.0.0
server.bolt.enabled=true
server.bolt.tls_level=DISABLED
server.bolt.listen_address=0.0.0.0:7687
server.http.enabled=true
server.http.listen_address=0.0.0.0:7474
server.https.enabled=false

# Directory Settings
server.directories.data=data
server.directories.plugins=plugins
server.directories.logs=logs
server.directories.import=import

# Memory Settings
server.memory.heap.initial_size=8G
server.memory.heap.max_size=8G
server.memory.pagecache.size=4G

# Security Settings
dbms.security.procedures.unrestricted=apoc.*,gds.*
dbms.security.auth_enabled=true
EOL

# Create apoc.conf
cat > neo4j-community-5.15.0/conf/apoc.conf << EOL
apoc.export.file.enabled=true
apoc.import.file.use_neo4j_config=false
apoc.import.file.enabled=true
EOL

# Add Neo4j to your PATH (add this to your ~/.bashrc)
echo 'export PATH="/home/$USER/arxiv-analysis/neo4j-community-5.15.0/bin:$PATH"' >> ~/.bashrc
echo 'alias neo4j-local="/home/$USER/arxiv-analysis/neo4j-community-5.15.0/bin/neo4j"' >> ~/.bashrc
source ~/.bashrc
```

3. Start Neo4j (use either method):
```bash
# Method 1: Using full path
./neo4j-community-5.15.0/bin/neo4j console

# Method 2: Using alias (after restarting terminal or sourcing .bashrc)
neo4j-local console
```

4. Access Neo4j:
- Browser interface: http://localhost:7474
- Bolt connection: bolt://localhost:7687
- Default credentials: 
  - Username: neo4j
  - Password: neo4j (you'll be prompted to change this on first login)

5. Environment Setup:
Create a `.env` file in your project root:
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_new_password  # Update this after changing the default password
```

Note: Make sure to add `.env` to your `.gitignore` to keep credentials secure:
```bash
echo ".env" >> .gitignore
```

## Common Issues

1. Python Version Mismatch:
   If you see a Python version error, make sure your Python version matches the one specified in `pyproject.toml`.

2. Neo4j Access Issues:
   - Ensure Neo4j is running (check console output)
   - Verify you're using the correct password in `.env`
   - Try accessing http://localhost:7474 in your browser
   - Check if the Neo4j process has permission to write to its directories

3. Path Issues:
   If `neo4j-local` command is not found:
   ```bash
   source ~/.bashrc  # Reload shell configuration
   # OR
   Use the full path: ./neo4j-community-5.15.0/bin/neo4j console
   ```
