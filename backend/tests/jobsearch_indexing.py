import unittest
import os
import sys

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.app.services.indexing_service import IndexingService
from backend.app.services.data_loader import load_documents

# Paths
data_file = "/Users/avishekanand/Projects/search-engine/data/documents/job_postings.csv.zip"
metadata_file = "/Users/avishekanand/Projects/search-engine/data/documents/metadata.csv"
temp_dir = "./temp_test"

# Load documents
documents = load_documents(data_file, metadata_file, temp_dir=temp_dir)
print(f"Loaded {len(documents)} documents.")

# Initialize indexing service
indexing_service = IndexingService(model_name="distiluse-base-multilingual-cased-v1", index_dir="./index")
indexing_service.create_embeddings(documents)