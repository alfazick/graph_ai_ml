from py2neo import Graph
import os
from dotenv import load_dotenv

def test_connection():
    try:
        # Load environment variables
        load_dotenv()

        # Get Neo4j connection details from environment variables
        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_user = os.getenv("NEO4J_USERNAME")
        neo4j_password = os.getenv("NEO4J_PASSWORD")

        # Connect to Neo4j
        graph = Graph(neo4j_uri, auth=(neo4j_user, neo4j_password))

        # Test connection
        result = graph.run("MATCH (n) RETURN count(n) as count").data()
        print(f"Successfully connected to Neo4j! Node count: {result[0]['count']}")
        
    except Exception as e:
        print(f"Error connecting to Neo4j: {e}")

if __name__ == "__main__":
    test_connection()
