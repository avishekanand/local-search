from fastapi import APIRouter, Query

router = APIRouter()

@router.get("/search")
def search(query: str = Query(..., description="Search query parameter")):
    """
    Dummy search endpoint that returns mock results.
    """
    return {
        "query": query,
        "results": [
            {"title": f"Document 1 for {query}", "snippet": "Snippet of document 3"},
            {"title": f"Document 2 for {query}", "snippet": "Snippet of document 2"},
        ],
    }
