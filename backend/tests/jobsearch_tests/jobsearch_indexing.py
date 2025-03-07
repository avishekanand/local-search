import unittest
import os
import sys
import yaml

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.app.services.indexing_service import IndexingService
from backend.app.services.data_loader import load_documents
# Path to the configuration file
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../config/config.yml"))

def load_config():
    """
    Loading the configuration from the YAML file.
    """
    with open(CONFIG_PATH, "r") as file:
        config = yaml.safe_load(file)
    return config

# Load configuration
config = load_config()

# # Extract relevant settings from config
# retrieval_model = config["retrieval"]["model"]
# index_directory = config["indexing"]["directory"]
# data_file = config["data"]["documents"]
# metadata_file = config["data"]["metadata"]
# temp_dir = config.get("indexing", {}).get("temp_dir", "./temp_test")  # Default to "./temp_test" if not in config
# field_to_index = config["indexing"]["field_to_index"]

# # Initialize QueryService with config values
# from backend.app.services.query_service import QueryService
# query_service = QueryService(model_name=retrieval_model, index_dir=index_directory)
# Paths
model_name = config["retrieval"]["model"]
index_dir = config["indexing"]["directory"]
field_to_index = config["indexing"]["field_to_index"]
temp_dir = config.get("indexing", {}).get("temp_dir", "./temp_test")  # Default to "./temp_test" if not in config
# Load documents
data_file = config["data"]["documents"]
metadata_file = config["data"]["metadata"]


documents = load_documents(data_file, metadata_file)

# Load documents
documents = load_documents(data_file, metadata_file, temp_dir=temp_dir)
print(f"Loaded {len(documents)} documents.")

# Index documents
# indexing_service = IndexingService(model_name=retrieval_model)
indexing_service = IndexingService(model_name=model_name, index_dir=index_dir, field_to_index=field_to_index)
indexing_service.create_embeddings(documents)