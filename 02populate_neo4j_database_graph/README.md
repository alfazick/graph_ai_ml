# Populating Neo4j Database

This guide explains how to populate the Neo4j database with the arXiv document similarity graph.

## Prerequisites

1. Neo4j Community Edition 5.15.0 installed
2. Generated CSV files from previous step (`nodes.csv` and `edges.csv`)

## Steps

### 1. Stop Neo4j Server (if running)
```bash
$NEO4J_HOME/bin/neo4j stop
```

Expected output:
```
Stopping Neo4j....... stopped.
```

### 2. Copy CSV Files
Copy the generated CSV files to Neo4j's import directory:
```bash
cp ../arxiv_analysis/data/nodes.csv ../arxiv_analysis/data/edges.csv import/
```

### 3. Import Data
Run the neo4j-admin import command:
```bash
./bin/neo4j-admin database import full --nodes=import/nodes.csv --relationships=import/edges.csv --overwrite-destination av-graph
```

Expected output:
```
Neo4j version: 5.15.0
Importing the contents of these files into [...]/neo4j-community-5.15.0/data/databases/av-graph:
Nodes:
  [...]/import/nodes.csv
Relationships:
  [...]/import/edges.csv

[...]

IMPORT DONE in 15s 310ms. 
Imported:
  50426 nodes
  25438455 relationships
  25589733 properties
Peak memory usage: 1.033GiB
```

### 4. Configure Neo4j

1. Edit `$NEO4J_HOME/conf/neo4j.conf`:
```bash
nano conf/neo4j.conf
```

2. Add or uncomment this line:
```conf
dbms.default_database=av-graph
```

### 5. Start Neo4j Server
```bash
$NEO4J_HOME/bin/neo4j start
```

### 6. Verify Import

1. Open Neo4j Browser at http://localhost:7474
2. Connect with default credentials (neo4j/neo4j)
3. Run these Cypher queries to check the data:

```cypher
// Count nodes
MATCH (n:Document) RETURN count(n);
// Expected: 50426 nodes

// Count relationships
MATCH ()-[r:SIMILAR_TO]->() RETURN count(r);
// Expected: 25438455 relationships

// Sample query to see document connections
MATCH (d:Document)-[r:SIMILAR_TO]->(other:Document)
WHERE d.documentId = "0704.0001"
RETURN d, r, other
LIMIT 5;
```

## Sample Queries

### Basic Exploration

```cypher
// List some papers to get an idea of the data
MATCH (d:Document) 
RETURN d.documentId, d.title, d.category
LIMIT 5;

// Get paper details by ID
MATCH (d:Document {documentId: "1805.02161"})
RETURN d.documentId, d.title, d.category;
```

### Finding Similar Papers

```cypher
// Find similar papers in specific categories (e.g., Machine Learning)
MATCH (d:Document)-[r:SIMILAR_TO]->(similar:Document)
WHERE 
    (d.category CONTAINS 'stat.ML' OR d.category CONTAINS 'cs.LG')
    AND (similar.category CONTAINS 'stat.ML' OR similar.category CONTAINS 'cs.LG')
RETURN d.documentId, d.title, similar.documentId, similar.title, r.similarity
ORDER BY r.similarity DESC
LIMIT 5;

// Find most similar papers to a specific paper
MATCH (d:Document {documentId: "1805.02161"})-[r:SIMILAR_TO]->(similar:Document)
RETURN d.title, d.category, similar.title, similar.category, r.similarity
ORDER BY r.similarity DESC
LIMIT 10;
```

### Network Analysis

```cypher
// Find papers with highest number of strong connections
MATCH (d:Document)-[r:SIMILAR_TO]->(similar:Document)
WHERE r.similarity > 0.8
WITH d, count(r) as strong_connections
RETURN d.documentId, d.title, d.category, strong_connections
ORDER BY strong_connections DESC
LIMIT 5;

// Find average similarity between different categories
MATCH (a:Document)-[r:SIMILAR_TO]->(b:Document)
WITH 
    CASE WHEN a.category = b.category THEN 'same_category' 
         ELSE 'different_category' END as connection_type,
    avg(r.similarity) as avg_similarity,
    count(*) as num_connections
RETURN connection_type, avg_similarity, num_connections;
```

These queries help explore the document similarity network. Some notes:
- Similarity scores range from 0 to 1, with 1 being most similar
- Categories are semicolon-separated (e.g., "stat.ML;cs.LG")
- Use the `CONTAINS` operator for category matching since papers can have multiple categories

## Performance Analysis

```cypher
// Check index usage
CALL db.stats.retrieve('GRAPH COUNTS');

// Check system info
CALL db.systemInfo();
```

## Graph Analysis

After importing the data, you can analyze the graph structure using our Python script:

```bash
# Make sure Neo4j is running
cd neo4j-community-5.15.0
./bin/neo4j start

# Run the analysis script
cd ../arxiv_analysis/src
python 04explore_graph.py
```

The script will generate a comprehensive markdown report in the `results` directory with:

1. Basic Graph Statistics
   - Total number of documents
   - Total number of relationships
   - Distribution of research categories

2. Machine Learning Papers Analysis
   - Finding similar papers in ML/Statistical Learning
   - Top similar paper pairs in these fields

3. Cross-Category Analysis
   - Comparing similarities within and across categories
   - Understanding interdisciplinary connections

4. Paper Clusters
   - Finding groups of highly related papers
   - Identifying research triangles with strong connections

The report will be saved as `graph_analysis_TIMESTAMP.md` and will contain detailed tables and descriptions for each analysis step.

## Troubleshooting

1. If import fails with "Database already exists":
   - Add `--overwrite-destination` flag to the import command
   - This will delete the existing database before import

2. If import fails with permission errors:
   - Ensure Neo4j has read access to CSV files
   - Check file ownership: `chown -R neo4j:neo4j $NEO4J_HOME/import`

3. If database doesn't start:
   - Check Neo4j logs: `$NEO4J_HOME/logs/neo4j.log`
   - Verify database name in neo4j.conf
   - Ensure enough disk space available

## Data Structure

### Nodes (Document)
- Properties:
  - `documentId`: arXiv ID (e.g., "0704.0001")
  - `title`: Document title
  - `category`: arXiv categories
  - `:LABEL`: Always "Document"

### Relationships (SIMILAR_TO)
- Properties:
  - `similarity`: Float value indicating document similarity
  - `:TYPE`: Always "SIMILAR_TO"
