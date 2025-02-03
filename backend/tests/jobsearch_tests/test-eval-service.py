import unittest
import os
import sys
import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import yaml

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# Path to the configuration file
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../config/config.yml"))

def load_config():
    """
    Load the configuration from the YAML file.
    """
    with open(CONFIG_PATH, "r") as file:
        config = yaml.safe_load(file)
    return config

config = load_config()

from backend.app.services.query_service import QueryService
from backend.app.services.evaluation_service import EvaluationService

# Extract settings for retrieval and indexing.
retrieval_model = config["retrieval"]["model"]
index_directory = config["indexing"]["directory"]

# Get evaluation settings from configuration.
ollama_config = config.get("ollama", {})
ollama_endpoint = ollama_config.get("endpoint", "http://localhost:11434/api/generate")
ollama_model = ollama_config.get("model", "deepseek-r1:8b")

# Initialize the QueryService with the specified model and index directory.
query_service = QueryService(model_name=retrieval_model, index_dir=index_directory)

# Initialize the EvaluationService with the Ollama endpoint and model.
evaluation_service = EvaluationService(endpoint=ollama_endpoint, model=ollama_model)

# Perform the search.
query = "Fachingenieur"  # Your query term
top_k = 20
results = query_service.search(query, top_k=top_k)

# Highlighting function: highlights query terms in the text output.
def highlight_query(text, query):
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    highlighted_text = pattern.sub(f"\033[1;32m{query}\033[0m", text)
    return highlighted_text

# Variables for precision computation.
relevant_count = 0.0  # We'll accumulate full credit (1.0) for "relevant" and half credit (0.5) for "partially relevant".

print(f"\n\033[1;34mQuery: {query}\033[0m")
print("\033[1;33mTop Results:\033[0m")

# Loop through the results, evaluate each, and count relevance.
for idx, result in enumerate(results, start=1):
    score = f"{result['score']:.2f}"
    title = highlight_query(result["metadata"]["title"], query)
    # Assume description is stored under metadata -> metadata with key "resposibilities"
    description_raw = result["metadata"]["metadata"].get("resposibilities", "")
    description = highlight_query(description_raw, query)

    print(f"\n\033[1;36mResult {idx}:\033[0m")
    print(f"  \033[1;35mScore:\033[0m {score}")
    print(f"  \033[1;35mTitle:\033[0m {title}")
    print(f"  \033[1;35mDescription:\033[0m {description}")
    
    # Evaluate the result using the EvaluationService.
    eval_result = evaluation_service.evaluate(query, result["metadata"]["title"], description_raw)
    print(f"  \033[1;35mEvaluation:\033[0m {eval_result}")
    
    # Count relevance based on the evaluation returned.
    # Here we assume: "relevant" counts as 1, "partially relevant" as 0.5.
    eval_lower = eval_result.lower()
    if eval_lower == "relevant":
        relevant_count += 1.0
    elif eval_lower == "partially relevant":
        relevant_count += 0.5

# Compute precision: relevant_count divided by total number of retrieved results.
precision = relevant_count / top_k if top_k > 0 else 0.0

print(f"\n\033[1;33mPrecision for query '{query}': {precision:.2f}\033[0m")