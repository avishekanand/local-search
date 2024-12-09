from fastapi import APIRouter, Query, HTTPException
from backend.app.services.query_service import QueryService
import os

router = APIRouter()

# Initialize QueryService
index_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../index"))
query_service = QueryService(model_name="distiluse-base-multilingual-cased-v1", index_dir=index_dir)

@router.get("/search")
def search(query: str = Query(..., description="Search query parameter"), top_k: int = 10):
    """
    Search endpoint that processes keyword queries and returns relevant results.
    """
    try:
        # Perform the search
        results = query_service.search(query=query, top_k=top_k)

        # Convert numpy.float32 to float for JSON serialization
        response = {
            "query": query,
            "results": [
                {
                    "title": result["metadata"]["title"],
                    "description:": result["metadata"]["metadata"].get("resposibilities", ""),
                    "score": float(result["score"]),  # Convert numpy.float32 to float
                }
                for result in results
            ],
        }
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {e}")