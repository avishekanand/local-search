import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
import logging
import time


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
        self.load_index()

    def load_index(self):
        """
        Load embeddings and metadata from index files ensuring matching numbers.
        """
        logger.info(f"Loading embeddings and metadata from {self.index_dir}...")
        
        # Collect all embeddings and metadata files
        embedding_files = sorted(
            [f for f in os.listdir(self.index_dir) if f.startswith("embeddings_") and f.endswith(".npy")]
        )
        metadata_files = sorted(
            [f for f in os.listdir(self.index_dir) if f.startswith("metadata_") and f.endswith(".json")]
        )

        # Ensure the number of files matches
        if len(embedding_files) != len(metadata_files):
            raise ValueError(f"Mismatch: {len(embedding_files)} embedding files and {len(metadata_files)} metadata files found.")

        # Check matching numbers in filenames
        for embedding_file, metadata_file in zip(embedding_files, metadata_files):
            embedding_number = int(embedding_file.split("_")[1].split(".")[0])
            metadata_number = int(metadata_file.split("_")[1].split(".")[0])

            if embedding_number != metadata_number:
                raise ValueError(f"Mismatch in file numbering: {embedding_file} and {metadata_file}")

            # Load the matched embedding and metadata
            embedding_path = os.path.join(self.index_dir, embedding_file)
            metadata_path = os.path.join(self.index_dir, metadata_file)

            self.embeddings.append(np.load(embedding_path))

            with open(metadata_path, "r") as f:
                self.metadata.extend(json.load(f))

        logger.info(f"Loaded {len(self.metadata)} documents, size of embeddings {len(self.embeddings)}.")
    # def _load_index(self):
    #     """
    #     Load embeddings and metadata from index files.
    #     """
    #     logger.info(f"Loading embeddings and metadata from {self.index_dir}...")
    #     for file in os.listdir(self.index_dir):
    #         if file.startswith("embeddings_") and file.endswith(".npy"):
    #             embedding_file = os.path.join(self.index_dir, file)
    #             self.embeddings.append(np.load(embedding_file))
    #         elif file.startswith("metadata_") and file.endswith(".json"):
    #             metadata_file = os.path.join(self.index_dir, file)
    #             with open(metadata_file, "r") as f:
    #                 self.metadata.extend(json.load(f))
    #     logger.info(f"Loaded {len(self.metadata)} documents, size of embeddings {len(self.embeddings)}.")

    def search(self, query: str, top_k: int = 1000):
        """
        Search for the top-k documents similar to the query.
        :param query: Query string.
        :param top_k: Number of top results to return.
        :return: List of top-k results with metadata.
        """
        start_time = time.perf_counter()  # Start timing

          # Encode the query
        query_embedding = self.model.encode(query, convert_to_numpy=True)
        end_time = time.perf_counter()  # End timing
        query_encoding_time = end_time - start_time  # Calculate elapsed time

        # Combine all embeddings into one array
        all_embeddings = np.vstack(self.embeddings)

        # Compute cosine similarity
        similarities = cosine_similarity([query_embedding], all_embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]  # Get top-k indices

        end_time = time.perf_counter()  # End timing
        processing_time = end_time - start_time  # Calculate elapsed time

        print(f"Query encoding time: {query_encoding_time:.4f} seconds and query processing time: {processing_time:.4f} seconds")  # Print

        logger.info(f"Size of similarities {len(similarities)} ")
        # Fetch corresponding metadata
        results = [{"score": similarities[i], "metadata": self.metadata[i]} for i in top_indices]
        return results