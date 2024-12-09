import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryService:
    def __init__(self, model_name: str, index_dir: str = "./index"):
        """
        Initialize the query service.
        :param model_name: Hugging Face model name for encoding.
        :param index_dir: Directory containing embeddings and metadata files.
        """
        self.model = SentenceTransformer(model_name)
        self.index_dir = index_dir
        self.embeddings = []
        self.metadata = []

        # Load all embeddings and metadata
        self._load_index()

    def _load_index(self):
        """
        Load embeddings and metadata from index files.
        """
        logger.info(f"Loading embeddings and metadata from {self.index_dir}...")
        for file in os.listdir(self.index_dir):
            if file.startswith("embeddings_") and file.endswith(".npy"):
                embedding_file = os.path.join(self.index_dir, file)
                self.embeddings.append(np.load(embedding_file))
            elif file.startswith("metadata_") and file.endswith(".json"):
                metadata_file = os.path.join(self.index_dir, file)
                with open(metadata_file, "r") as f:
                    self.metadata.extend(json.load(f))
        logger.info(f"Loaded {len(self.metadata)} documents.")

    def search(self, query: str, top_k: int = 10):
        """
        Search for the top-k documents similar to the query.
        :param query: Query string.
        :param top_k: Number of top results to return.
        :return: List of top-k results with metadata.
        """
        # Encode the query
        query_embedding = self.model.encode(query, convert_to_numpy=True)

        # Combine all embeddings into one array
        all_embeddings = np.vstack(self.embeddings)

        # Compute cosine similarity
        similarities = cosine_similarity([query_embedding], all_embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]  # Get top-k indices

        # Fetch corresponding metadata
        results = [{"score": similarities[i], "metadata": self.metadata[i]} for i in top_indices]
        return results