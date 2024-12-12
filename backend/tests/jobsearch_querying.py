import unittest
import os
import sys
import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.app.services.query_service import QueryService

# Query Service Initialization
query_service = QueryService(model_name="distiluse-base-multilingual-cased-v1", index_dir="./index")

# Perform Search
query = "it engineer"  # Your query term
top_k = 10
results = query_service.search(query, top_k=top_k)

# Highlighting Function
def highlight_query(text, query):
    """
    Highlights the query term in the text using ANSI escape codes.
    """
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    highlighted_text = pattern.sub(f"\033[1;32m{query}\033[0m", text)
    return highlighted_text

# Validation Function
def validate_results(query, results, query_service):
    """
    Validates the results by encoding the query and titles and computing cosine similarity.
    Reports differences between reported and computed scores.
    """
    # Encode the query
    query_embedding = query_service.model.encode(query, convert_to_numpy=True)

    # Validate each result
    for idx, result in enumerate(results, start=1):
        title = result["metadata"]["title"]
        reported_score = result["score"]
        if title:
            # Encode the title
            title_embedding = query_service.model.encode(title, convert_to_numpy=True)

            # Compute cosine similarity
            validated_score = cosine_similarity([query_embedding], [title_embedding])[0][0]

            # Report validation
            print(f"\n\033[1;36mValidation for Result {idx}:\033[0m")
            print(f"  \033[1;35mTitle:\033[0m {title}")
            print(f"  \033[1;35mReported Score:\033[0m {reported_score:.4f}")
            print(f"  \033[1;35mValidated Score:\033[0m {validated_score:.4f}")

            # Check for discrepancies
            if abs(reported_score - validated_score) > 0.01:
                print("\033[1;31m  Warning:\033[0m Significant difference between reported and validated scores!")

# Display Results
print(f"\n\033[1;34mQuery: {query}\033[0m")
print("\033[1;33mTop Results:\033[0m")
for idx, result in enumerate(results, start=1):
    score = f"{result['score']:.2f}"
    title = highlight_query(result["metadata"]["title"], query)
    description = highlight_query(result["metadata"]["metadata"].get("resposibilities", ""), query)

    print(f"\n\033[1;36mResult {idx}:\033[0m")
    print(f"  \033[1;35mScore:\033[0m {score}")
    print(f"  \033[1;35mTitle:\033[0m {title}")
    print(f"  \033[1;35mDescription:\033[0m {description}")

# Validate Results
print("\n\033[1;33mValidating Results...\033[0m")
validate_results(query, results, query_service)