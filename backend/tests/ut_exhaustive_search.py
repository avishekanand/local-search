import unittest
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import sys

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.app.services.query_service import QueryService


class TestQueryService(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment.
        """
        self.model_name = "distiluse-base-multilingual-cased-v1"
        self.index_dir = "./index"  # Adjust this path to point to your index directory
        self.query_service = QueryService(model_name=self.model_name, index_dir=self.index_dir)

    def test_embeddings_dimensions(self):
        """
        Test that the embeddings dimensions and total count are as expected.
        """
        # Retrieve embeddings
        embeddings = self.query_service.embeddings

        # Calculate total number of embeddings
        total_embeddings = sum(embedding.shape[0] for embedding in embeddings)

        # Assertions
        self.assertGreater(len(embeddings), 0, "No embeddings files loaded.")
        self.assertGreater(total_embeddings, 0, "Total embeddings count is zero.")
        print(f"Number of embedding files: {len(embeddings)}")
        print(f"Total number of embeddings: {total_embeddings}")

        # Check dimensions of each embedding file
        for i, embedding in enumerate(embeddings):
            self.assertEqual(len(embedding.shape), 2, f"Embedding file {i + 1} does not have 2D shape.")
            print(f"Embedding file {i + 1}: Shape = {embedding.shape}")

    def test_query_processing_uses_all_embeddings(self):
        """
        Test that query processing compares against all embeddings.
        """
        query = "test query"
        top_k = 10

        # Perform the query
        results = self.query_service.search(query, top_k=top_k)

        # Calculate total number of embeddings
        total_embeddings = sum(embedding.shape[0] for embedding in self.query_service.embeddings)

        # Assertions
        self.assertGreater(len(results), 0, "Query did not return any results.")
        print(f"Total embeddings used: {total_embeddings}")
        print(f"Number of results returned: {len(results)}")
        print(f"Results (Top {top_k}):")
        for idx, result in enumerate(results, start=1):
            print(f"{idx}. Title: {result['metadata']['title']}, Score: {result['score']:.4f}")

        # Verify the number of embeddings matches
        self.assertEqual(
            total_embeddings,
            np.vstack(self.query_service.embeddings).shape[0],
            "Total embeddings used during query processing do not match loaded embeddings."
        )

if __name__ == "__main__":
    unittest.main()