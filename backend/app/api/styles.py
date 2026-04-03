"""Genre style retrieval endpoint (D-11)."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.services.rag_retriever import get_collection, query_styles

router = APIRouter()


@router.get("/styles")
async def styles(
    prompt: str = Query(..., description="Text prompt to match against genre styles"),
    n_results: int = Query(3, ge=1, le=10, description="Number of results to return"),
) -> list[dict]:
    """Return matched genre-style documents for a prompt.

    Public debug endpoint for testing RAG retrieval before rendering.
    """
    collection = get_collection()
    return query_styles(collection, prompt, n_results=n_results)
