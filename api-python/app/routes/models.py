"""
Models routes for AI model management.
"""
from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.models.user import User
from app.middleware.auth import get_current_active_user

router = APIRouter(prefix="/api/models", tags=["models"])


class ModelInfo(BaseModel):
    """Schema for model information."""
    id: str
    name: str
    endpoint: str
    capabilities: List[str] = []


@router.get("/", response_model=List[ModelInfo])
async def get_models(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get available AI models.

    TODO: Query actual model configurations from database/config.
    """
    # Placeholder model list
    models = [
        ModelInfo(
            id="gpt-4",
            name="GPT-4",
            endpoint="openai",
            capabilities=["chat", "completion"],
        ),
        ModelInfo(
            id="gpt-3.5-turbo",
            name="GPT-3.5 Turbo",
            endpoint="openai",
            capabilities=["chat", "completion"],
        ),
        ModelInfo(
            id="claude-3-opus",
            name="Claude 3 Opus",
            endpoint="anthropic",
            capabilities=["chat"],
        ),
    ]

    return models
