import os
import json
import logging
from typing import List
from sentence_transformers import SentenceTransformer
from backend.app.services.data_loader import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndexingService:
    def __init__(self, model_name: str, index_dir: str = "./index", batch_size: int = 25000):
        """
        Initialize the indexing service.
        :param model_name: Hugging Face model name for encoding.
        :param index_dir: Directory to store the index files.
        :param batch_size: Number of embeddings per file.
        """
        self.model = SentenceTransformer(model_name)
        self.index_dir = index_dir
        self.batch_size = batch_size

        # Ensure the index directory exists
        os.makedirs(self.index_dir, exist_ok=True)

    def create_embeddings(self, documents: List[Document]) -> None:
        """
        Create and store embeddings for the title field of the documents.
        :param documents: List of Document objects to process.
        """
        logger.info(f"Starting to create embeddings for {len(documents)} documents...")
        titles = [doc.title for doc in documents if doc.title]

        logger.info(f"Encoding {len(titles)} titles using model {self.model}.")
        embeddings = self.model.encode(titles, show_progress_bar=True, convert_to_numpy=True)

        # Split embeddings into chunks of `batch_size` and save to files
        total_files = (len(embeddings) + self.batch_size - 1) // self.batch_size
        logger.info(f"Storing embeddings in {total_files} files, each containing up to {self.batch_size} embeddings.")

        for i in range(total_files):
            start = i * self.batch_size
            end = min(start + self.batch_size, len(embeddings))
            batch_embeddings = embeddings[start:end]

            # Write the batch to a JSON file
            file_path = os.path.join(self.index_dir, f"embeddings_{i + 1}.json")
            with open(file_path, "w") as f:
                json.dump(batch_embeddings.tolist(), f)

            logger.info(f"Stored embeddings {start}-{end} in file: {file_path}")

        logger.info(f"All embeddings have been processed and stored in {self.index_dir}.")