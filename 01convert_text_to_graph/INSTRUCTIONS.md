# ArXiv Analysis Project Instructions

## Project Setup

1. Clone the data repository:
```bash
# Get access to the Manning LiveProject repository with the dataset
git clone [repository-url] temp-data
```

2. Set up data directory:
```bash
# Copy the data file to your project's data directory
cp temp-data/data/stat-abstracts.tsv arxiv_analysis/data/
```

3. Install required spaCy model:
```bash
poetry run python -m spacy download en_core_web_md
```

## Data Preparation Steps

### 1. Loading and Examining the Data

The data is stored in TSV (Tab-Separated Values) format with the following columns:
- doc_id: ArXiv document identifier
- title: Paper title
- category: Paper categories (semicolon-separated)
- abstract: Full paper abstract

Example code to load and examine the data (`01data_prep.py`):
```python
import pandas as pd

# Configure pandas display
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 50)  # Truncate long text (abstracts)

# Load the TSV file
df = pd.read_csv("path/to/stat-abstracts.tsv", sep="\t", header=None)
df.columns = ["doc_id", "title", "category", "abstract"]
```

### Next Steps
- Process paper categories
- Create document embeddings using spaCy
- Build graph structures
- Generate adjacency matrices

*This document will be updated as we progress through the project.*
