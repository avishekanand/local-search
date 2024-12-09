import unittest
import os
import sys

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.app.services.query_service import QueryService

query_service = QueryService(model_name="distiluse-base-multilingual-cased-v1", index_dir="./index")
results = query_service.search("example query", top_k=5)

# Display results
for result in results:
    print(f"Score: {result['score']}")
    print(f"Title: {result['metadata']['title']}")
    print(f"Metadata: {result['metadata']['metadata']}")