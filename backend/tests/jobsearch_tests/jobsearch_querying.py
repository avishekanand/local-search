# import unittest
# import os
# import sys
# import re
# import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity
# import yaml

# # Add the project root directory to sys.path
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# # Path to the configuration file
# CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../config/config.yml"))

# def load_config():
#     """
#     Loading the configuration from the YAML file.
#     """
#     with open(CONFIG_PATH, "r") as file:
#         config = yaml.safe_load(file)
#     return config

# config = load_config()

# from backend.app.services.query_service import QueryService

# # Extract relevant settings
# retrieval_model = config["retrieval"]["model"]
# index_directory = config["indexing"]["directory"]

# # Initialize QueryService with config values
# query_service = QueryService(model_name=retrieval_model, index_dir=index_directory)

# # Perform Search
# query = "Fachingenieur"  # Your query term
# top_k = 20
# results = query_service.search(query, top_k=top_k)

# # Highlighting Function
# def highlight_query(text, query):
#     """
#     Highlights the query term in the text using ANSI escape codes.
#     """
#     pattern = re.compile(re.escape(query), re.IGNORECASE)
#     highlighted_text = pattern.sub(f"\033[1;32m{query}\033[0m", text)
#     return highlighted_text

# # Validation Function
# def validate_results(query, results, query_service):
#     """
#     Validates the results by encoding the query and titles and computing cosine similarity.
#     Reports differences between reported and computed scores.
#     """
#     # Encode the query
#     query_embedding = query_service.model.encode(query, convert_to_numpy=True)

#     # Validate each result
#     for idx, result in enumerate(results, start=1):
#         title = result["metadata"]["title"]
#         reported_score = result["score"]
#         if title:
#             # Encode the title
#             title_embedding = query_service.model.encode(title, convert_to_numpy=True)

#             # Compute cosine similarity
#             validated_score = cosine_similarity([query_embedding], [title_embedding])[0][0]

#             # Report validation
#             print(f"\n\033[1;36mValidation for Result {idx}:\033[0m")
#             print(f"  \033[1;35mTitle:\033[0m {title}")
#             print(f"  \033[1;35mReported Score:\033[0m {reported_score:.4f}")
#             print(f"  \033[1;35mValidated Score:\033[0m {validated_score:.4f}")

#             # Check for discrepancies
#             if abs(reported_score - validated_score) > 0.01:
#                 print("\033[1;31m  Warning:\033[0m Significant difference between reported and validated scores!")

# # Display Results
# print(f"\n\033[1;34mQuery: {query}\033[0m")
# print("\033[1;33mTop Results:\033[0m")
# for idx, result in enumerate(results, start=1):
#     score = f"{result['score']:.2f}"
#     title = highlight_query(result["metadata"]["title"], query)
#     description = highlight_query(result["metadata"]["metadata"].get("resposibilities", ""), query)

#     print(f"\n\033[1;36mResult {idx}:\033[0m")
#     print(f"  \033[1;35mScore:\033[0m {score}")
#     print(f"  \033[1;35mTitle:\033[0m {title}")
#     print(f"  \033[1;35mDescription:\033[0m {description}")

# # Validate Results
# # print("\n\033[1;33mValidating Results...\033[0m")
# # validate_results(query, results, query_service)

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

# Highlighting function: Highlights query terms in the text output.
def highlight_query(text, query):
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    highlighted_text = pattern.sub(f"\033[1;32m{query}\033[0m", text)
    return highlighted_text

# Validation function: (Optional) Compares reported vs. computed cosine similarity.
def validate_results(query, results, query_service):
    query_embedding = query_service.model.encode(query, convert_to_numpy=True)
    for idx, result in enumerate(results, start=1):
        title = result["metadata"]["title"]
        reported_score = result["score"]
        if title:
            title_embedding = query_service.model.encode(title, convert_to_numpy=True)
            validated_score = cosine_similarity([query_embedding], [title_embedding])[0][0]
            print(f"\n\033[1;36mValidation for Result {idx}:\033[0m")
            print(f"  \033[1;35mTitle:\033[0m {title}")
            print(f"  \033[1;35mReported Score:\033[0m {reported_score:.4f}")
            print(f"  \033[1;35mValidated Score:\033[0m {validated_score:.4f}")
            if abs(reported_score - validated_score) > 0.01:
                print("\033[1;31m  Warning:\033[0m Significant difference between reported and validated scores!")

# Display and evaluate the results.
print(f"\n\033[1;34mQuery: {query}\033[0m")
print("\033[1;33mTop Results:\033[0m")
for idx, result in enumerate(results, start=1):
    score = f"{result['score']:.2f}"
    title = highlight_query(result["metadata"]["title"], query)
    # Extract the raw description from metadata. (Key name might vary; here we use "resposibilities".)
    description_raw = result["metadata"]["metadata"].get("resposibilities", "")
    description = highlight_query(description_raw, query)

    print(f"\n\033[1;36mResult {idx}:\033[0m")
    print(f"  \033[1;35mScore:\033[0m {score}")
    print(f"  \033[1;35mTitle:\033[0m {title}")
    print(f"  \033[1;35mDescription:\033[0m {description}")
    
    # Evaluate the result using the EvaluationService.
    eval_result = evaluation_service.evaluate(query, result["metadata"]["title"], description_raw)
    print(f"  \033[1;35mEvaluation:\033[0m {eval_result}")

# (Optional) Validate the results by comparing cosine similarities.
# print("\n\033[1;33mValidating Results...\033[0m")
# validate_results(query, results, query_service)