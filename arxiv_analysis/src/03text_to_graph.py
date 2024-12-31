import os
import pandas as pd
from scipy.sparse import load_npz
from tqdm import tqdm

def create_nodes_csv(abstracts_path: str, output_path: str):
    """Create nodes.csv with document ID, title, and category."""
    print("Reading documents...")
    df = pd.read_csv(abstracts_path, sep='\t', usecols=[0,1,2], names=['paper_id', 'title', 'categories'])
    
    print("Creating nodes dataframe...")
    nodes_df = pd.DataFrame({
        'documentId:ID': df['paper_id'],
        'title': df['title'],
        'category': df['categories'],
        ':LABEL': 'Document'
    })
    
    print("Saving nodes to CSV...")
    nodes_df.to_csv(output_path, index=False)
    print(f"Created nodes.csv with {len(nodes_df):,} documents")

def create_edges_csv(sparse_matrix_path: str, doc_ids: list, output_path: str):
    """Create edges.csv directly from sparse matrix data."""
    print("\nLoading sparse matrix...")
    adj_matrix = load_npz(sparse_matrix_path)
    
    print("Converting to edges...")
    rows, cols = adj_matrix.nonzero()
    similarities = adj_matrix.data
    
    print(f"Found {len(similarities):,} edges")
    
    print("Creating edges dataframe...")
    edges = []
    for i, j, sim in tqdm(zip(rows, cols, similarities), total=len(similarities), desc="Processing edges"):
        edges.append({
            ':START_ID': doc_ids[i],
            ':END_ID': doc_ids[j],
            'similarity:float': float(sim),
            ':TYPE': 'SIMILAR_TO'
        })
    
    print("Saving edges to CSV...")
    edges_df = pd.DataFrame(edges)
    edges_df.to_csv(output_path, index=False)
    print(f"Created edges.csv with {len(edges_df):,} relationships")

def main():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    paths = {
        'in': {
            'abstracts': os.path.join(data_dir, "stat-abstracts.tsv"),
            'matrix': os.path.join(data_dir, "av-adjmatrix.npz"),
            'docids': os.path.join(data_dir, "stat-av-docids.txt")
        },
        'out': {
            'nodes': os.path.join(data_dir, "nodes.csv"),
            'edges': os.path.join(data_dir, "edges.csv")
        }
    }
    
    print("\n1. Creating nodes.csv...")
    create_nodes_csv(paths['in']['abstracts'], paths['out']['nodes'])
    
    print("\n2. Loading document IDs...")
    with open(paths['in']['docids'], 'r') as f:
        doc_ids = [line.strip() for line in f]
    
    print("\n3. Creating edges.csv...")
    create_edges_csv(paths['in']['matrix'], doc_ids, paths['out']['edges'])
    
    print("\nDone! Created files:")
    print(f"- {paths['out']['nodes']}")
    print(f"- {paths['out']['edges']}")

if __name__ == "__main__":
    main()
