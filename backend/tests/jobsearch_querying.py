import unittest
import os
import sys
import re

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.app.services.query_service import QueryService

# Query Service Initialization
query_service = QueryService(model_name="distiluse-base-multilingual-cased-v1", index_dir="./index")

# Perform Search
query = "Netzwerk"  # Your query term
top_k = 5
results = query_service.search(query, top_k=top_k)

# Highlighting Function
def highlight_query(text, query):
    """
    Highlights the query term in the text using ANSI escape codes.
    """
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    highlighted_text = pattern.sub(f"\033[1;32m{query}\033[0m", text)
    return highlighted_text

# Display Results
print(f"\n\033[1;34mQuery: {query}\033[0m")
print("\033[1;33mTop Results:\033[0m")
for idx, result in enumerate(results, start=1):
    score = f"{result['score']:.2f}"
    title = highlight_query(result["metadata"]["title"], query)
    description = highlight_query(result["metadata"]["metadata"].get("description", ""), query)

    print(f"\n\033[1;36mResult {idx}:\033[0m")
    print(f"  \033[1;35mScore:\033[0m {score}")
    print(f"  \033[1;35mTitle:\033[0m {title}")
    print(f"  \033[1;35mDescription:\033[0m {description}")