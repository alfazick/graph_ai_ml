from abc import ABC, abstractmethod
import numpy as np
from typing import List


class EmbeddingModel(ABC):
    """Abstract base class for text embedding models."""
    
    @abstractmethod
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get embedding vectors for multiple texts.
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            numpy.ndarray: Matrix of embedding vectors
        """
        pass
    
    @abstractmethod
    def get_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute similarity between two embedding vectors.
        
        Args:
            vec1: First embedding vector
            vec2: Second embedding vector
            
        Returns:
            float: Similarity score between the vectors
        """
        pass
