# Minimal GCP Setup for ArXiv Analysis

## Prerequisites
- Google Cloud Platform account
- `gcloud` CLI tool installed and configured
- Project ID with billing enabled

## VM Creation
```bash
gcloud compute instances create arxiv-analysis \
  --project=your-project-id \
  --zone=us-central1-a \
  --machine-type=e2-standard-8 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-ssd

# Allow Neo4j ports
gcloud compute firewall-rules create allow-neo4j \
  --allow tcp:7474,tcp:7687
```

## System Setup

### 1. Connect to VM
```bash
gcloud compute ssh arxiv-analysis
```

### 2. Install System Requirements
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install basic requirements
sudo apt install -y build-essential python3-pip openjdk-11-jdk

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Install and Configure Neo4j
```bash
# Download Neo4j
wget https://dist.neo4j.org/neo4j-community-5.15.0-unix.tar.gz

# Extract Neo4j
tar -xf neo4j-community-5.15.0-unix.tar.gz

# Create a configuration file
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

# Add Neo4j to your PATH (add this to your ~/.bashrc)
echo 'export PATH="/home/$USER/arxiv-analysis/neo4j-community-5.15.0/bin:$PATH"' >> ~/.bashrc
echo 'alias neo4j-local="/home/$USER/arxiv-analysis/neo4j-community-5.15.0/bin/neo4j"' >> ~/.bashrc
source ~/.bashrc

# Start Neo4j (use either of these commands)
./neo4j-community-5.15.0/bin/neo4j console  # Using full path
# OR
neo4j-local console  # Using alias (after restarting terminal or sourcing .bashrc)
```

### 4. Configure APOC
Create a new file `neo4j-community-5.15.0/conf/apoc.conf`:
```properties
apoc.export.file.enabled=true
apoc.import.file.use_neo4j_config=false
apoc.import.file.enabled=true
```

### 5. Access Neo4j
After starting Neo4j:
1. Open http://localhost:7474 in your browser
2. Login with default credentials:
   - Username: `neo4j`
   - Password: `neo4j`
3. You'll be prompted to change the password on first login

### 6. Set Up Environment Variables
Create a `.env` file in your project root:
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_secure_password
```

Add `.env` to `.gitignore`:
```bash
echo ".env" >> .gitignore
```

### 7. Test Connection
Run the test script:
```bash
python test_neo4j.py
```

The script will use environment variables to connect to Neo4j:
```python
from py2neo import Graph
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Neo4j connection details
neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")

# Connect to Neo4j
graph = Graph(neo4j_uri, auth=(neo4j_user, neo4j_password))
```

## Project Setup

### 1. Create Project Structure
```bash
mkdir ~/arxiv-analysis && cd ~/arxiv-analysis
mkdir -p arxiv_analysis/{data,src}
```

### 2. Configure Poetry Project
```bash
# Initialize Poetry project
poetry init -n

# Create pyproject.toml with current versions
cat > pyproject.toml << EOL
[tool.poetry]
name = "arxiv-analysis"
version = "0.1.0"
description = "ArXiv statistics papers analysis"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.10"
matplotlib = "^3.7.1"
networkx = "^3.1"
numpy = "^1.24.0"
pandas = "^2.0.0"
spacy = "^3.6.0"
py2neo = "^2021.2.3"
umap-learn = "^0.5.3"
hdbscan = "^0.8.29"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
EOL
```

### 3. Install Dependencies
```bash
# Install project dependencies
poetry install

# Install spaCy model
poetry run python -m spacy download en_core_web_md
```

## Verification Steps

1. Check Neo4j Status:
```bash
sudo systemctl status neo4j
```

2. Access Neo4j Browser:
   - Open http://localhost:7474 in your browser
   - Default credentials: neo4j/neo4j
   - You'll be prompted to change password on first login

3. Verify Python Environment:
```bash
poetry shell
python -c "import spacy, pandas, networkx; print('Setup successful!')"
```

## Security Notes
1. Never commit `.env` file to version control
2. Use strong passwords for Neo4j
3. Consider enabling TLS in production
4. Restrict GCP firewall rules to necessary IP ranges
5. Keep Neo4j updated with security patches

## Troubleshooting
1. If Neo4j browser connection fails:
   - Verify VM's external IP is correct
   - Check if ports 7474 and 7687 are open in GCP firewall
   - Ensure Neo4j is running: `sudo systemctl status neo4j`

2. If Python connection fails:
   - Verify environment variables in `.env`
   - Check if `python-dotenv` is installed
   - Ensure Neo4j password matches `.env` file

3. For permission issues:
   - Check Neo4j logs: `sudo tail -f /var/log/neo4j/neo4j.log`
   - Verify file permissions: `sudo chown -R neo4j:neo4j /var/lib/neo4j/`

## Final Result
You should now have:
1. A GCP VM with:
   - Ubuntu 22.04 LTS
   - Python 3.10+
   - Neo4j database
2. Python environment with all required data science packages
3. Project structure ready for ArXiv analysis
4. Neo4j accessible at http://localhost:7474
