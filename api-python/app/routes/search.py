"""
Search routes for Meilisearch integration.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from app.models.user import User
from app.middleware.auth import get_current_active_user
from app.utils.logger import logger

router = APIRouter(prefix="/api/search", tags=["search"])


class SearchResult(BaseModel):
    """Schema for search result."""
    id: str
    type: str  # "message", "conversation", etc.
    title: Optional[str] = None
    content: Optional[str] = None
    conversationId: Optional[str] = None
    score: float = 0.0


@router.get("/", response_model=List[SearchResult])
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    type: Optional[str] = Query(None, description="Result type filter"),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
):
    """
    Search across messages and conversations.

    TODO: Integrate with Meilisearch for full-text search.
    """
    # Placeholder - actual implementation needs Meilisearch client
    logger.warning("Meilisearch not integrated, returning empty results")
    return []
