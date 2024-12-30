import unittest
import numpy as np
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.SpacyEmbModel import SpacyEmbModel


class TestSpacyEmbModel(unittest.TestCase):
    
    def setUp(self):
        """Set up SpaCy model before each test."""
        self.model = SpacyEmbModel("en_core_web_md")
        
    def test_get_embeddings_shape(self):
        """Test if embeddings have correct shape."""
        texts = ["hello world", "test text"]
        embeddings = self.model.get_embeddings(texts)
        
        # SpaCy's en_core_web_md has 300-dimensional vectors
        self.assertEqual(embeddings.shape, (2, 300))
        
    def test_get_embeddings_consistency(self):
        """Test if same text produces same embedding."""
        text = ["hello world"]
        emb1 = self.model.get_embeddings(text)
        emb2 = self.model.get_embeddings(text)
        
        np.testing.assert_array_almost_equal(emb1, emb2)
        
    def test_similarity_same_vector(self):
        """Test if similarity of vector with itself is 1."""
        text = ["hello world"]
        emb = self.model.get_embeddings(text)
        similarity = self.model.get_similarity(emb[0], emb[0])
        
        self.assertAlmostEqual(similarity, 1.0)
        
    def test_similarity_range(self):
        """Test if similarity is between -1 and 1."""
        texts = ["hello world", "completely different text"]
        emb = self.model.get_embeddings(texts)
        similarity = self.model.get_similarity(emb[0], emb[1])
        
        self.assertGreaterEqual(similarity, -1.0)
        self.assertLessEqual(similarity, 1.0)


if __name__ == '__main__':
    unittest.main()
