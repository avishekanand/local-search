import os
import sys
import json
import numpy as np
import logging
from typing import List
from sentence_transformers import SentenceTransformer

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
print(sys.path)

from backend.app.services.data_loader import Document

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class IndexingService:
    def __init__(self, model_name: str, index_dir: str = "./index", batch_size: int = 25000, field_to_index: str = "title"):
        """
        Initialize the indexing service.
        :param model_name: Hugging Face model name for encoding.
        :param index_dir: Directory to store the index files.
        :param batch_size: Number of embeddings per file.
        :param field_to_index: The text field in metadata to index.
        """
        self.model = SentenceTransformer(model_name)
        self.index_dir = index_dir
        self.batch_size = batch_size
        self.field_to_index = field_to_index  # Field to index
        os.makedirs(self.index_dir, exist_ok=True)

    def create_embeddings(self, documents: List[dict]) -> None:
        """
        Create and store embeddings for the specified field of the documents.
        Metadata includes the indexed field and additional information.
        :param documents: List of Document objects to process.
        """
        logger.info(f"Starting to create embeddings for {len(documents)} documents...")

        # Extract the field to be indexed and the metadata
        field_texts = [getattr(doc, self.field_to_index, None) for doc in documents if getattr(doc, self.field_to_index, None)]
        skipped_docs = [doc for doc in documents if not getattr(doc, self.field_to_index, None)]
        logger.info(f"Skipped {len(skipped_docs)} documents without '{self.field_to_index}' field.")

        metadata = [
            {
                "id": i,
                self.field_to_index: getattr(doc, self.field_to_index, ""),
                "metadata": {key: value for key, value in vars(doc).items() if value is not None}
            }
            for i, doc in enumerate(documents) if getattr(doc, self.field_to_index, None)
        ]

        # Encode the text field to create embeddings
        logger.info(f"Encoding {len(field_texts)} documents for field '{self.field_to_index}' using model {self.model}.")
        embeddings = self.model.encode(field_texts, show_progress_bar=True, convert_to_numpy=True)

        # Split embeddings and metadata into chunks
        total_files = (len(embeddings) + self.batch_size - 1) // self.batch_size
        logger.info(f"Storing embeddings in {total_files} files, each containing up to {self.batch_size} embeddings.")

        for i in range(total_files):
            start = i * self.batch_size
            end = min(start + self.batch_size, len(embeddings))

            batch_embeddings = embeddings[start:end]
            batch_metadata = metadata[start:end]

            # Save embeddings
            embedding_file = os.path.join(self.index_dir, f"embeddings_{i + 1}.npy")
            np.save(embedding_file, batch_embeddings)

            # Save metadata
            metadata_file = os.path.join(self.index_dir, f"metadata_{i + 1}.json")
            with open(metadata_file, "w") as f:
                json.dump(batch_metadata, f)

            logger.info(f"Stored embeddings {start}-{end} in file: {embedding_file}")
            logger.info(f"Stored metadata {start}-{end} in file: {metadata_file}")

        logger.info(f"All embeddings and metadata for field '{self.field_to_index}' have been processed and stored in {self.index_dir}.")

    def _validate_index(self):
        """
        Validate that all embedding files and metadata files are consistent.
        """
        logger.info(f"Validating index files in {self.index_dir}...")
        embedding_files = sorted([f for f in os.listdir(self.index_dir) if f.startswith("embeddings_") and f.endswith(".npy")])
        metadata_files = sorted([f for f in os.listdir(self.index_dir) if f.startswith("metadata_") and f.endswith(".json")])

        for i, (embedding_file, metadata_file) in enumerate(zip(embedding_files, metadata_files)):
            embedding_path = os.path.join(self.index_dir, embedding_file)
            metadata_path = os.path.join(self.index_dir, metadata_file)

            # Load embeddings and metadata
            embeddings = np.load(embedding_path)
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            logger.debug(f"File {i + 1}: Embedding shape: {embeddings.shape}, Metadata count: {len(metadata)}")

            # Ensure alignment
            assert embeddings.shape[0] == len(metadata), (
                f"Mismatch in embeddings and metadata for file {embedding_file}. "
                f"Embeddings: {embeddings.shape[0]}, Metadata: {len(metadata)}"
            )

        logger.info("Index validation complete. All files are consistent.")