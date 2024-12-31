#!/usr/bin/env python3
"""
Explore the arXiv document similarity graph using Neo4j.
Connects to Neo4j and runs various analysis queries.
"""

from py2neo import Graph, Node, Relationship, NodeMatcher
import pandas as pd
from tabulate import tabulate
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from collections import Counter, defaultdict

class GraphExplorer:
    def __init__(self):
        """Initialize connection to Neo4j using environment variables."""
        load_dotenv()
        
        # Get Neo4j connection details from environment variables
        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_user = os.getenv("NEO4J_USERNAME")
        neo4j_password = os.getenv("NEO4J_PASSWORD")
        
        if not all([neo4j_uri, neo4j_user, neo4j_password]):
            raise ValueError("Missing Neo4j connection details in environment variables")
            
        self.graph = Graph(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.matcher = NodeMatcher(self.graph)
        
        # Initialize report content
        self.report_content = []
        
    def _setup_report_file(self) -> str:
        """Create and return path for the report file."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        results_dir = os.path.join(current_dir, "..", "results")
        os.makedirs(results_dir, exist_ok=True)
        
        # Remove old reports
        for item in os.listdir(results_dir):
            if item.startswith("graph_analysis_") and item.endswith(".md"):
                os.remove(os.path.join(results_dir, item))
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(results_dir, f"graph_analysis_{timestamp}.md")
    
    def add_to_report(self, section: str, df: pd.DataFrame = None, description: str = None):
        """Add a section to the report."""
        self.report_content.append(f"\n## {section}\n")
        
        if description:
            self.report_content.append(f"{description}\n")
        
        if df is not None:
            self.report_content.append("```")
            self.report_content.append(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
            self.report_content.append("```\n")
    
    def explore_basic_stats(self):
        """Get basic statistics about the graph."""
        self.add_to_report("Step 1: Basic Graph Statistics", 
                          description="Overview of the document graph structure and size.")
        
        # Get total documents
        total_docs = len(self.matcher.match("Document"))
        docs_df = pd.DataFrame([{"document_count": total_docs}])
        self.add_to_report("Total Documents", docs_df, 
                          "Number of research papers in the graph.")
        
        # Get total relationships
        total_rels = self.graph.evaluate("MATCH ()-[r:SIMILAR_TO]->() RETURN count(r)")
        rels_df = pd.DataFrame([{"relationship_count": total_rels}])
        self.add_to_report("Total Relationships", rels_df,
                          "Number of similarity connections between papers.")
        
        # Get category distribution
        categories = []
        for doc in self.matcher.match("Document").limit(1000):
            if doc["category"]:
                categories.extend(doc["category"].split(";"))
        
        category_counts = Counter(categories).most_common(10)
        cat_df = pd.DataFrame(category_counts, columns=["category", "count"])
        self.add_to_report("Category Distribution", cat_df,
                          "Top 10 research categories by number of papers.")

    def explore_ml_papers(self):
        """Explore machine learning papers and their connections."""
        self.add_to_report("Step 2: Machine Learning Papers Analysis",
                          description="Analysis of papers in Machine Learning and Statistical Learning categories.")
        
        ml_papers = []
        for doc in self.matcher.match("Document").limit(1000):
            category = doc.get("category", "")
            if "stat.ML" in category or "cs.LG" in category:
                similar = self.graph.match((doc, ), r_type="SIMILAR_TO").limit(10)
                for rel in similar:
                    end_node = rel.end_node
                    end_category = end_node.get("category", "")
                    if "stat.ML" in end_category or "cs.LG" in end_category:
                        ml_papers.append({
                            "source_id": doc["documentId"],
                            "source_title": doc["title"],
                            "target_id": end_node["documentId"],
                            "target_title": end_node["title"],
                            "similarity": rel["similarity"]
                        })
        
        ml_df = pd.DataFrame(ml_papers)
        if not ml_df.empty:
            ml_df = ml_df.sort_values("similarity", ascending=False).head(10)
            self.add_to_report("Most Similar ML Papers", ml_df,
                             "Top 10 most similar pairs of Machine Learning papers.")

    def explore_cross_category_connections(self):
        """Analyze connections between different categories."""
        self.add_to_report("Step 3: Cross-Category Analysis",
                          description="Analysis of similarities between papers from same vs different categories.")
        
        same_cat = defaultdict(list)
        diff_cat = defaultdict(list)
        
        for rel in self.graph.match(r_type="SIMILAR_TO").limit(1000):
            start_cat = rel.start_node.get("category", "")
            end_cat = rel.end_node.get("category", "")
            similarity = rel["similarity"]
            
            if start_cat == end_cat:
                same_cat["similarities"].append(similarity)
            else:
                diff_cat["similarities"].append(similarity)
        
        results = []
        if same_cat["similarities"]:
            results.append({
                "connection_type": "same_category",
                "avg_similarity": round(sum(same_cat["similarities"]) / len(same_cat["similarities"]), 4),
                "num_connections": len(same_cat["similarities"])
            })
        
        if diff_cat["similarities"]:
            results.append({
                "connection_type": "different_category",
                "avg_similarity": round(sum(diff_cat["similarities"]) / len(diff_cat["similarities"]), 4),
                "num_connections": len(diff_cat["similarities"])
            })
        
        df = pd.DataFrame(results)
        self.add_to_report("Category Connection Analysis", df,
                          "Comparison of similarity scores between papers from same vs different categories.")

    def find_paper_clusters(self):
        """Find papers that form strongly connected clusters."""
        self.add_to_report("Step 4: Paper Clusters",
                          description="Finding groups of three papers that are all highly similar to each other (similarity > 0.9).")
        
        clusters = []
        processed = set()
        
        for doc in self.matcher.match("Document").limit(500):
            if doc["documentId"] in processed:
                continue
            
            similar1 = [(rel.end_node, rel["similarity"]) 
                       for rel in self.graph.match((doc, ), r_type="SIMILAR_TO")
                       if rel["similarity"] > 0.9]
            
            for paper2, sim1 in similar1:
                if paper2["documentId"] <= doc["documentId"]:
                    continue
                
                similar2 = [(rel.end_node, rel["similarity"]) 
                           for rel in self.graph.match((paper2, ), r_type="SIMILAR_TO")
                           if rel["similarity"] > 0.9 and rel.end_node != doc]
                
                for paper3, sim2 in similar2:
                    if paper3["documentId"] <= paper2["documentId"]:
                        continue
                    
                    for rel in self.graph.match((paper3, ), r_type="SIMILAR_TO"):
                        if rel.end_node == doc and rel["similarity"] > 0.9:
                            clusters.append({
                                "paper1_id": doc["documentId"],
                                "paper2_id": paper2["documentId"],
                                "paper3_id": paper3["documentId"],
                                "category1": doc["category"],
                                "category2": paper2["category"],
                                "category3": paper3["category"],
                                "avg_similarity": (sim1 + sim2 + rel["similarity"]) / 3
                            })
                            processed.add(doc["documentId"])
                            processed.add(paper2["documentId"])
                            processed.add(paper3["documentId"])
                            break
                    
                    if len(clusters) >= 5:
                        break
                if len(clusters) >= 5:
                    break
            if len(clusters) >= 5:
                break
        
        df = pd.DataFrame(clusters)
        if not df.empty:
            df = df.sort_values("avg_similarity", ascending=False)
            self.add_to_report("Strong Paper Clusters", df,
                             "Top 5 clusters of three papers with high similarity to each other.")

    def save_report(self):
        """Save the final report."""
        report_path = self._setup_report_file()
        
        # Add header
        header = f"""# arXiv Document Graph Analysis Report
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This report analyzes the similarity relationships between arXiv research papers.
"""
        
        # Combine all content
        full_report = [header] + self.report_content
        
        # Save report
        with open(report_path, 'w') as f:
            f.write('\n'.join(full_report))
        
        print(f"\nReport saved to: {report_path}")
        return report_path

def main():
    try:
        # Initialize explorer
        explorer = GraphExplorer()
        
        # Run various analyses
        print("\nExploring arXiv Document Similarity Graph...")
        print("=" * 50)
        
        explorer.explore_basic_stats()
        explorer.explore_ml_papers()
        explorer.explore_cross_category_connections()
        explorer.find_paper_clusters()
        
        # Save final report
        report_path = explorer.save_report()
        print("\nAnalysis complete! Report has been saved to:")
        print(report_path)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
