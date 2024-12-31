"""
Validation script for adjacency matrix generation.
Compares document IDs and matrix contents between temp and final data
to ensure data integrity during the graph construction process.
"""

import os
import numpy as np
from scipy.sparse import load_npz

# Paths
TEMP_DATA_DIR = "/home/nurbekoff/arxiv-analysis/temp-data/data"
DATA_DIR = "/home/nurbekoff/arxiv-analysis/arxiv_analysis/data"

def ensure_data_dir():
    """Create data directory if it doesn't exist"""
    if not os.path.exists(DATA_DIR):
        print(f"\nCreating data directory at {DATA_DIR}")
        os.makedirs(DATA_DIR)

def list_files(directory):
    """List all files in directory"""
    print(f"\nFiles in {directory}:")
    if not os.path.exists(directory):
        print("Directory does not exist!")
        return
    
    for f in os.listdir(directory):
        path = os.path.join(directory, f)
        size = os.path.getsize(path)
        print(f"- {f} ({size:,} bytes)")

def compare_docids():
    print("\nComparing docids files...")
    temp_docids = os.path.join(TEMP_DATA_DIR, "stat-av-docids.txt")
    our_docids = os.path.join(DATA_DIR, "stat-av-docids.txt")
    
    if not os.path.exists(temp_docids):
        print(f"Reference docids file doesn't exist at {temp_docids}")
        return
        
    if not os.path.exists(our_docids):
        print(f"Our docids file doesn't exist at {our_docids}")
        print("Please run the data preparation script first to generate this file.")
        return
    
    with open(temp_docids, 'r') as f1, open(our_docids, 'r') as f2:
        temp_lines = f1.readlines()
        our_lines = f2.readlines()
        
        if len(temp_lines) != len(our_lines):
            print(f"Different number of lines! Reference: {len(temp_lines):,}, Ours: {len(our_lines):,}")
            return
            
        differences = 0
        for i, (l1, l2) in enumerate(zip(temp_lines, our_lines)):
            if l1 != l2:
                differences += 1
                if differences <= 5:  # Show first 5 differences
                    print(f"Line {i} differs:")
                    print(f"Reference: {l1.strip()}")
                    print(f"Ours     : {l2.strip()}")
        
        if differences == 0:
            print("✓ docids files are identical!")
        else:
            print(f"✗ Total {differences:,} lines differ")

def compare_matrices():
    print("\nComparing adjacency matrices...")
    temp_matrix = os.path.join(TEMP_DATA_DIR, "av-adjmatrix.npz")
    our_matrix = os.path.join(DATA_DIR, "av-adjmatrix.npz")
    
    if not os.path.exists(temp_matrix):
        print(f"Reference matrix file doesn't exist at {temp_matrix}")
        return
        
    if not os.path.exists(our_matrix):
        print(f"Our matrix file doesn't exist at {our_matrix}")
        print("Please run the data preparation script first to generate this file.")
        return
        
    ref_sparse = load_npz(temp_matrix)
    our_sparse = load_npz(our_matrix)
    
    print(f"\nReference matrix: shape={ref_sparse.shape}, nonzeros={ref_sparse.nnz:,}")
    print(f"Our matrix: shape={our_sparse.shape}, nonzeros={our_sparse.nnz:,}")
    
    if ref_sparse.shape != our_sparse.shape:
        print("✗ Matrices have different shapes!")
        return
        
    if ref_sparse.nnz != our_sparse.nnz:
        print("✗ Matrices have different number of nonzero elements!")
        return
        
    # Convert to dense for comparison (only small sections)
    sample_size = 1000
    print(f"\nComparing {sample_size:,} random elements...")
    
    np.random.seed(42)  # For reproducible sampling
    rand_rows = np.random.randint(0, ref_sparse.shape[0], sample_size)
    rand_cols = np.random.randint(0, ref_sparse.shape[1], sample_size)
    
    ref_samples = ref_sparse[rand_rows, rand_cols].toarray()
    our_samples = our_sparse[rand_rows, rand_cols].toarray()
    
    if np.array_equal(ref_samples, our_samples):
        print(f"✓ All {sample_size:,} sampled elements are identical!")
    else:
        diff = np.sum(ref_samples != our_samples)
        print(f"✗ {diff:,} differences found in {sample_size:,} sampled elements")

if __name__ == "__main__":
    print("Starting comparison...")
    print(f"TEMP_DATA_DIR: {TEMP_DATA_DIR}")
    print(f"DATA_DIR: {DATA_DIR}")
    
    # List files in both directories
    list_files(TEMP_DATA_DIR)
    list_files(DATA_DIR)
    
    # Ensure data directory exists
    ensure_data_dir()
    
    # Compare files
    compare_docids()
    compare_matrices()
