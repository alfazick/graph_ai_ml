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

### 2. Import Data
Run the neo4j-admin import command:
```bash
$NEO4J_HOME/bin/neo4j-admin database import full --nodes=nodes.csv --relationships=edges.csv av-graph
```

This command:
- Creates a new database named 'av-graph'
- Imports nodes from nodes.csv
- Imports relationships from edges.csv
- Uses 'full' mode for a fresh database

### 3. Configure Neo4j

1. Edit `$NEO4J_HOME/conf/neo4j.conf`:
   ```conf
   # Set initial database
   dbms.default_database=av-graph
   ```

### 4. Start Neo4j Server
```bash
$NEO4J_HOME/bin/neo4j start
# Or for console output:
$NEO4J_HOME/bin/neo4j console
```

### 5. Verify Import

1. Open Neo4j Browser at http://localhost:7474
2. Connect with default credentials (neo4j/neo4j)
3. Run these Cypher queries to check the data:

```cypher
// Count nodes
MATCH (n:Document) RETURN count(n);

// Count relationships
MATCH ()-[r:SIMILAR_TO]->() RETURN count(r);

// Sample query to see document connections
MATCH (d:Document)-[r:SIMILAR_TO]->(other:Document)
WHERE d.documentId = "0704.0001"
RETURN d, r, other
LIMIT 5;
```

## Data Structure

### Nodes (Document)
- Properties:
  - documentId: arXiv ID (e.g., "0704.0001")
  - title: Document title
  - category: arXiv categories

### Relationships (SIMILAR_TO)
- Properties:
  - similarity: Float value indicating document similarity

## Troubleshooting

1. If import fails with permission errors:
   - Ensure Neo4j has read access to CSV files
   - Check file ownership: `chown -R neo4j:neo4j $NEO4J_HOME/import`

2. If database doesn't start:
   - Check Neo4j logs: `$NEO4J_HOME/logs/neo4j.log`
   - Verify database name in neo4j.conf
   - Ensure enough disk space available
