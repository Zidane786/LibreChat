"""
Prompt routes for managing prompt library.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.prompt import Prompt, PromptGroup
from app.models.user import User
from app.middleware.auth import get_current_active_user
from app.utils.logger import logger

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


class PromptCreate(BaseModel):
    """Schema for creating a prompt."""
    name: str = Field(..., max_length=100)
    content: str
    category: Optional[str] = None
    tags: List[str] = []


class PromptResponse(BaseModel):
    """Schema for prompt response."""
    id: str
    name: str
    content: str
    category: Optional[str] = None
    tags: List[str] = []
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[PromptResponse])
async def get_prompts(
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
):
    """Get all prompts for the user."""
    try:
        query = Prompt.find(Prompt.user == current_user.id)
        if category:
            query = query.find(Prompt.category == category)

        prompts = await query.to_list()
        return [PromptResponse(id=str(p.id), **p.dict()) for p in prompts]

    except Exception as e:
        logger.error(f"Error fetching prompts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching prompts",
        )


@router.post("/", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    prompt_data: PromptCreate,
    current_user: User = Depends(get_current_active_user),
):
    """Create a new prompt."""
    try:
        prompt = Prompt(user=current_user.id, **prompt_data.dict())
        await prompt.insert()

        return PromptResponse(id=str(prompt.id), **prompt.dict())

    except Exception as e:
        logger.error(f"Error creating prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating prompt",
        )


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
    prompt_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Delete a prompt."""
    try:
        prompt = await Prompt.find_one(
            Prompt.id == prompt_id,
            Prompt.user == current_user.id,
        )

        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prompt not found",
            )

        await prompt.delete()
        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting prompt",
        )
