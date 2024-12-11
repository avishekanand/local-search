from fastapi import APIRouter, Query, HTTPException
from backend.app.services.query_service import QueryService
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize QueryService
index_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../index"))

if not os.path.exists(index_dir):
    raise HTTPException(status_code=500, detail=f"Index directory '{index_dir}' not found.")
query_service = QueryService(model_name="distiluse-base-multilingual-cased-v1", index_dir=index_dir)

from fastapi import APIRouter, Query, HTTPException
import logging
import json
from backend.app.services.query_service import QueryService
import os

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize QueryService
index_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../index"))
query_service = QueryService(model_name="distiluse-base-multilingual-cased-v1", index_dir=index_dir)

@router.get("/search")
def search(query: str = Query(..., description="Search query parameter"), top_k: int = 20):
    """
    Search endpoint that processes keyword queries and returns relevant results.
    """
    try:
        logger.info(f"Received search query: {query} with top_k: {top_k}")

        # Perform the search
        results = query_service.search(query=query, top_k=top_k)
        logger.info(f"Search completed. Number of results: {len(results)}")

        # Build the response
        response = {
            "query": query,
            "results": [
                {
                    "title": result["metadata"].get("title", "No Title"),
                    "requirements": result["metadata"]["metadata"].get("requirements", ""),
                    "description": result["metadata"]["metadata"].get("resposibilities", ""),
                    "score": float(result["score"]),  # Convert numpy.float32 to float
                }
                for result in results
            ],
        }

        # Debugging the response
        logger.debug("Generated Response: %s", json.dumps(response, indent=2))  # Logs the response as formatted JSON

        return response

    except Exception as e:
        logger.error(f"Error processing query '{query}': {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {e}")
