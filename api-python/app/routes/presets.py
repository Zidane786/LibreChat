"""
Presets routes for conversation presets.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.preset import Preset
from app.models.user import User
from app.middleware.auth import get_current_active_user
from app.utils.logger import logger

router = APIRouter(prefix="/api/presets", tags=["presets"])


class PresetCreate(BaseModel):
    """Schema for creating a preset."""
    name: str = Field(..., max_length=100)
    endpoint: str
    model: str
    temperature: Optional[float] = 0.7
    maxTokens: Optional[int] = None


class PresetResponse(BaseModel):
    """Schema for preset response."""
    id: str
    name: str
    endpoint: str
    model: str
    temperature: Optional[float] = None
    maxTokens: Optional[int] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[PresetResponse])
async def get_presets(
    current_user: User = Depends(get_current_active_user),
):
    """Get all presets for the user."""
    try:
        presets = await Preset.find(Preset.user == current_user.id).to_list()
        return [PresetResponse(id=str(p.id), **p.dict()) for p in presets]

    except Exception as e:
        logger.error(f"Error fetching presets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching presets",
        )


@router.post("/", response_model=PresetResponse, status_code=status.HTTP_201_CREATED)
async def create_preset(
    preset_data: PresetCreate,
    current_user: User = Depends(get_current_active_user),
):
    """Create a new preset."""
    try:
        preset = Preset(user=current_user.id, **preset_data.dict())
        await preset.insert()

        return PresetResponse(id=str(preset.id), **preset.dict())

    except Exception as e:
        logger.error(f"Error creating preset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating preset",
        )


@router.delete("/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preset(
    preset_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Delete a preset."""
    try:
        preset = await Preset.find_one(
            Preset.id == preset_id,
            Preset.user == current_user.id,
        )

        if not preset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Preset not found",
            )

        await preset.delete()
        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting preset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting preset",
        )
