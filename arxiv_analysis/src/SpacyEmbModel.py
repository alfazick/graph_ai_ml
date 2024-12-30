import spacy
import numpy as np
from typing import List
from src.embedding_model import EmbeddingModel


class SpacyEmbModel(EmbeddingModel):
    """SpaCy implementation of the embedding model."""
    
    def __init__(self, model_name: str):
        """Initialize SpaCy model.
        
        Args:
            model_name: Name of the spaCy model (e.g., 'en_core_web_md')
        """
        self.nlp = spacy.load(model_name)
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get embedding vectors for multiple texts using SpaCy.
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            numpy.ndarray: Matrix of document vectors
        """
        # Process all texts with SpaCy
        docs = list(self.nlp.pipe(texts))
        
        # Get document vectors
        vectors = np.array([doc.vector for doc in docs])
        return vectors
    
    def get_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors.
        
        Args:
            vec1: First embedding vector
            vec2: Second embedding vector
            
        Returns:
            float: Cosine similarity score between the vectors
        """
        # Compute cosine similarity
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)