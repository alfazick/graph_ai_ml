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

## Project Structure

```
arxiv_analysis/
├── src/
│   ├── __init__.py
│   ├── embedding_model.py     # Abstract base class for embeddings
│   ├── SpacyEmbModel.py      # SpaCy implementation
│   ├── dataloader.py         # Data loading utilities
│   └── 01data_prep.py        # Main data preparation script
├── tests/
│   └── test_embeddings.py    # Unit tests for embedding functionality
└── data/
    └── stat-abstracts.tsv    # Dataset (not in git)
```

## Implementation Steps

### 1. Data Loading and Examination

```python
from dataloader import DataLoader

# Load the TSV file with columns
columns = ["doc_id", "title", "category", "abstract"]
df = DataLoader().load_data(ABSTRACT_FILE, "tsv", columns)
```

### 2. Text Embeddings

We use SpaCy's medium English model for generating document embeddings:

```python
from src.SpacyEmbModel import SpacyEmbModel

# Initialize the embedding model
emb_model = SpacyEmbModel("en_core_web_md")

# Get embeddings for texts
embeddings = emb_model.get_embeddings(texts)

# Compute similarity between vectors
similarity = emb_model.get_similarity(vec1, vec2)
```

### 3. Running Tests

To run the embedding tests:
```bash
cd arxiv_analysis/tests
poetry run python test_embeddings.py
```

The tests verify:
- Correct embedding dimensions (300D for en_core_web_md)
- Embedding consistency
- Similarity computation
- Valid similarity range [-1, 1]

### Next Steps
- Process all paper abstracts to create embeddings
- Build graph structure using similarity scores
- Generate adjacency matrices
- Implement graph analysis algorithms

*This document will be updated as we progress through the project.*
