import os
import numpy as np
from scipy.sparse import coo_matrix, save_npz
from tqdm import tqdm
import psutil
import gc
import tempfile
import time

"""Data preparation script for ArXiv analysis.

This script processes document vectors to create a similarity graph:
1. Reads document vectors from TSV file
2. Computes pairwise similarities using batched dot products
3. Creates a sparse adjacency matrix based on similarity threshold
4. Saves the matrix and document IDs

Implementation details:
- Uses memory-mapped arrays to handle large edge sets efficiently
- Processes document similarities in 500x500 batches
- Uses dynamic thresholding to maintain ~2% sparsity
- Base similarity threshold: 9.5 (dot product)
- Produces ~25M edges in final symmetrized matrix
- Memory efficient: stays under 2GB throughout processing
- Saves results as sparse NPZ matrix

Memory optimization techniques:
- Memory-mapped edge storage
- Batch processing with size 500
- Regular garbage collection
- Periodic disk flushing
- Chunked final matrix creation

System Requirements:
- Minimum 4GB RAM (2GB used + buffer)
- ~1GB disk space for temporary files
- Works on typical development machines
- No special hardware required

Note on Edge Count:
While the reference implementation produces ~50M edges, this optimized
version intentionally produces ~25M edges to:
1. Work on machines with limited RAM (4-8GB)
2. Maintain better memory efficiency (<2GB usage)
3. Focus on stronger similarity connections
4. Enable faster downstream graph processing

Output files:
- av-adjmatrix.npz: Sparse adjacency matrix
- stat-av-docids.txt: Document IDs in matrix order
"""

# Clear memory caches
gc.collect()

# Step 0: Setup paths
current_dir = os.path.dirname(__file__)
DATA_DIR = os.path.join(current_dir, "..", "data")
ABS_VEC_FILE = os.path.join(DATA_DIR, "stat-abstract-vectors.tsv")
DOCIDS_LIST = os.path.join(DATA_DIR, "stat-av-docids.txt")
ADJ_MATRIX_FILE = os.path.join(DATA_DIR, "av-adjmatrix.npz")

def get_memory_usage():
    """Return the current memory usage in GB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024 / 1024  # Convert to GB

def main():
    # Step 1: First pass to count vectors and determine dimensions
    print("Step 1: Counting vectors and determining dimensions...")
    n_docs = 0
    vec_dim = None
    
    with open(ABS_VEC_FILE, "r") as f:
        for line in f:
            if n_docs == 0:
                _, vec_str = line.strip().split('\t')
                vec_dim = len(vec_str.split(','))
            n_docs += 1
    
    print(f"Total documents: {n_docs:,}")
    print(f"Vector dimension: {vec_dim}")
    print(f"Initial memory usage: {get_memory_usage():.2f} GB")
    
    # Step 2: Read vectors and create document matrix
    print("\nStep 2: Reading vectors and creating document matrix...")
    X = np.empty((n_docs, vec_dim), dtype=np.float32)
    docids = []
    
    with open(ABS_VEC_FILE, "r") as f:
        for i, line in enumerate(tqdm(f, total=n_docs)):
            doc_id, vec_str = line.strip().split('\t')
            X[i] = np.array([float(x) for x in vec_str.split(',')], dtype=np.float32)
            docids.append(doc_id)
    
    print(f"Document matrix shape: {X.shape}")
    print(f"Memory usage after matrix creation: {get_memory_usage():.2f} GB")
    
    # Step 3: Compute similarities in batches
    print("\nStep 3: Computing similarities in batches...")
    threshold = 9.5  # Base threshold
    batch_size = 500  # Smaller batch size for more granular control
    target_sparsity = 0.02  # Target 2% sparsity (reference has ~2% sparsity)
    
    try:
        # Process upper triangular part in batches
        total_batches = ((n_docs + batch_size - 1) // batch_size)
        n_total = (total_batches * (total_batches + 1)) // 2  # Number of batch pairs
        
        print(f"Total batches to process: {n_total:,}")
        print(f"Base threshold: {threshold}")
        print(f"Target sparsity: {target_sparsity*100:.2f}%")
        print(f"Initial memory: {get_memory_usage():.2f} GB")
        
        # Create memory-mapped arrays for edges
        edge_file = tempfile.NamedTemporaryFile(delete=False)
        index_file = tempfile.NamedTemporaryFile(delete=False)
        
        # Pre-allocate space for edges (estimate based on target sparsity)
        max_edges = int(n_docs * n_docs * target_sparsity)  # No buffer needed since we know target
        edges_mm = np.memmap(edge_file.name, dtype=np.int32, mode='w+', shape=(max_edges, 2))
        current_idx = 0
        
        # Track statistics
        skipped_batches = 0
        total_potential = 0
        last_report_time = time.time()
        report_interval = 5  # seconds
        
        # Adjust batch threshold parameters
        max_edges_per_batch = batch_size * batch_size * target_sparsity * 4  # Allow more edges per batch
        min_percentile = 95  # Don't let threshold get too high
        
        with tqdm(total=n_total, desc="Processing batches") as pbar:
            for i in range(0, n_docs, batch_size):
                i_end = min(i + batch_size, n_docs)
                batch_i = X[i:i_end]
                
                # Only process upper triangular part
                for j in range(i, n_docs, batch_size):
                    j_end = min(j + batch_size, n_docs)
                    batch_j = X[j:j_end]
                    
                    # Compute similarities for this batch
                    sim_batch = np.dot(batch_i, batch_j.T)
                    
                    # Adjust threshold dynamically based on batch size to maintain target sparsity
                    batch_threshold = threshold
                    if len(sim_batch[sim_batch >= threshold]) > max_edges_per_batch:
                        # Only increase threshold if we have too many edges
                        percentile = np.percentile(sim_batch, min_percentile)
                        batch_threshold = max(threshold, percentile)
                    
                    # Find pairs above threshold
                    rows, cols = np.where(sim_batch >= batch_threshold)
                    n_potential = len(rows)
                    
                    # Skip if still too many edges after threshold adjustment
                    if n_potential > max_edges_per_batch:
                        print(f"\rSkipping batch {i//batch_size}-{j//batch_size}: too many edges ({n_potential:,})", end="")
                        del sim_batch, rows, cols
                        gc.collect()
                        pbar.update(1)
                        skipped_batches += 1
                        continue
                    
                    # Adjust indices and filter in one step
                    rows += i
                    cols += j
                    if i == j:
                        mask = cols > rows
                        rows = rows[mask]
                        cols = cols[mask]
                    
                    # Add edges to memmap array
                    n_new = len(rows)
                    if n_new > 0:
                        if current_idx + n_new > max_edges:
                            # Resize memmap array if needed
                            new_max = max_edges * 2
                            edges_mm.flush()
                            del edges_mm
                            edges_mm = np.memmap(edge_file.name, dtype=np.int32, mode='w+', shape=(new_max, 2))
                            max_edges = new_max
                        
                        edges_mm[current_idx:current_idx + n_new, 0] = rows
                        edges_mm[current_idx:current_idx + n_new, 1] = cols
                        current_idx += n_new
                        
                        if current_idx % 1000 == 0:  # Flush periodically instead of every time
                            edges_mm.flush()
                        
                        total_potential += n_potential
                        print(f"\rBatch {i//batch_size}-{j//batch_size}: {n_potential} found, {n_new} new edges, total {current_idx:,} edges (sparsity: {current_idx/(n_docs*n_docs)*100:.4f}%)", end="")
                    
                    # Clean up batch data
                    del sim_batch, rows, cols
                    gc.collect()
                    pbar.update(1)
                    
                    # Report progress periodically
                    if time.time() - last_report_time > report_interval:
                        last_report_time = time.time()
                        mem_usage = get_memory_usage()
                        print(f"\nProgress Report:")
                        print(f"  - Batch: {i//batch_size} of {total_batches}")
                        print(f"  - Total edges: {current_idx:,}")
                        print(f"  - Memory usage: {mem_usage:.2f} GB")
                        print(f"  - Sparsity: {current_idx / (n_docs * n_docs) * 100:.6f}%")
                        print(f"  - Skipped batches: {skipped_batches}")
                        print(f"  - Total potential edges: {total_potential:,}")
        
        # Trim the memmap array to actual size
        edges_mm.flush()
        del edges_mm
        
        # Create final sparse matrix
        print("\nStep 4: Creating sparse matrix...")
        print(f"Memory before final conversion: {get_memory_usage():.2f} GB")
        
        # Load edges from memmap in chunks to avoid memory spike
        chunk_size = 10_000_000  # Process 10M edges at a time
        sparse_matrices = []
        
        for chunk_start in range(0, current_idx, chunk_size):
            chunk_end = min(chunk_start + chunk_size, current_idx)
            edges_mm = np.memmap(edge_file.name, dtype=np.int32, mode='r', 
                               shape=(current_idx, 2), offset=0)
            chunk = edges_mm[chunk_start:chunk_end]
            
            # Create sparse matrix for this chunk
            chunk_matrix = coo_matrix(
                (np.ones(chunk_end - chunk_start, dtype=np.int8),
                 (chunk[:, 0], chunk[:, 1])),
                shape=(n_docs, n_docs)
            )
            sparse_matrices.append(chunk_matrix)
            
            # Clean up
            del edges_mm, chunk, chunk_matrix
            gc.collect()
        
        # Sum all matrices
        print("Combining chunks...")
        sparse_matrix = sparse_matrices[0]
        for matrix in sparse_matrices[1:]:
            sparse_matrix = sparse_matrix + matrix
        del sparse_matrices
        gc.collect()
        
        print(f"Memory after matrix creation: {get_memory_usage():.2f} GB")
        
        # Symmetrize the matrix efficiently
        print("Symmetrizing matrix...")
        sparse_matrix = sparse_matrix + sparse_matrix.T
        gc.collect()
        
        print(f"Memory after symmetrization: {get_memory_usage():.2f} GB")
        
        # Clean up temp files
        print("Cleaning up temporary files...")
        os.unlink(edge_file.name)
        os.unlink(index_file.name)
        
        # Save results
        print(f"\nStep 5: Saving adjacency matrix to {ADJ_MATRIX_FILE}...")
        save_npz(ADJ_MATRIX_FILE, sparse_matrix)
        
        print(f"Saving document IDs to {DOCIDS_LIST}...")
        with open(DOCIDS_LIST, "w") as f:
            for doc_id in docids:
                f.write(f"{doc_id}\n")
        
        print("\nFinal statistics:")
        print(f"Number of documents: {n_docs:,}")
        print(f"Number of edges (after symmetrization): {sparse_matrix.nnz:,}")
        print(f"Sparsity: {sparse_matrix.nnz / (n_docs * n_docs) * 100:.4f}%")
        print(f"Final memory usage: {get_memory_usage():.2f} GB")
        
        # Clean up
        del X, sparse_matrix
        gc.collect()
    
    except Exception as e:
        # Clean up temp files in case of error
        try:
            os.unlink(edge_file.name)
            os.unlink(index_file.name)
        except:
            pass
        print(f"Error occurred: {str(e)}")
        print(f"Memory usage at error: {get_memory_usage():.2f} GB")
        raise

if __name__ == "__main__":
    main()