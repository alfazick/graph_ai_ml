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
# Install Neo4j
curl -fsSL https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt update && sudo apt install -y neo4j

# Configure Neo4j
sudo nano /etc/neo4j/neo4j.conf

# Add these configurations:
server.default_listen_address=0.0.0.0
dbms.security.procedures.unrestricted=apoc.*,gds.*
server.memory.heap.initial_size=8G
server.memory.heap.max_size=8G
server.memory.pagecache.size=4G

# Network Settings - Allow External Connections
server.bolt.enabled=true
server.bolt.tls_level=DISABLED
server.bolt.listen_address=0.0.0.0:7687

# HTTP Settings
server.http.enabled=true
server.http.listen_address=0.0.0.0:7474

# Start Neo4j
sudo systemctl start neo4j
sudo systemctl enable neo4j
```

### 4. Configure APOC
Create a new file `/etc/neo4j/conf/apoc.conf`:
```properties
apoc.export.file.enabled=true
apoc.import.file.use_neo4j_config=false
apoc.import.file.enabled=true
```

### 5. Set Up Environment Variables
Create a `.env` file in your project root:
```bash
NEO4J_URI=bolt://<YOUR-VM-IP>:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_secure_password
```

Add `.env` to `.gitignore`:
```bash
echo ".env" >> .gitignore
```

### 6. Change Default Password
1. Access Neo4j Browser at `http://<YOUR-VM-IP>:7474`
2. Login with default credentials:
   - Username: `neo4j`
   - Password: `neo4j`
3. Set a new password when prompted
4. Update the password in your `.env` file

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

### 8. Accessing Neo4j Browser in Firefox

1. Start Neo4j:
```bash
cd ~/neo4j/neo4j-community-5.15.0
./bin/neo4j console
```

2. Open Mozilla Firefox and navigate to:
```
http://<YOUR-VM-IP>:7474
```
Replace `<YOUR-VM-IP>` with your VM's external IP (e.g., http://34.59.148.10:7474)

3. In the Neo4j Browser connection screen:
   - Connection URL: `bolt://<YOUR-VM-IP>:7687` (e.g., bolt://34.59.148.10:7687)
   - Username: `neo4j`
   - Password: `neo4j` (first time only, you'll be prompted to change it)

4. After changing the password, update your `.env` file with the new password.

Note: The password will persist as long as the data directory (`~/neo4j/neo4j-community-5.15.0/data`) remains intact. If you delete this directory, you'll need to set a new password.

### Troubleshooting Browser Connection
1. If the connection fails:
   - Verify Neo4j is running (`neo4j console` should show no errors)
   - Check if ports 7474 and 7687 are open in your GCP firewall rules
   - Make sure you're using `http://` for browser and `bolt://` for connection
   - Try clearing Firefox cache and cookies for the Neo4j Browser page

2. If you get a password error:
   - Check if the data directory exists and has content
   - If it's empty, you'll need to use the default password (`neo4j`) and set a new one
   - After setting the password, update your `.env` file to match

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
   - Open http://VM_IP:7474 in your browser
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
4. Neo4j accessible at http://VM_IP:7474
