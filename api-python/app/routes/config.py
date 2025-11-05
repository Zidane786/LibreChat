"""
Config routes for system configuration.
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.models.user import User
from app.middleware.auth import get_current_active_user
from app.config import get_settings

router = APIRouter(prefix="/api/config", tags=["config"])


class ConfigResponse(BaseModel):
    """Schema for config response."""
    appTitle: str
    endpoints: Dict[str, Any] = {}
    modelSpecs: Dict[str, Any] = {}
    interface: Dict[str, Any] = {}


@router.get("/", response_model=ConfigResponse)
async def get_config(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get system configuration.

    Returns configuration for:
    - Available AI endpoints
    - Model specifications
    - UI interface settings
    """
    settings = get_settings()

    # Build config response
    # TODO: Populate from actual endpoint configurations
    config = ConfigResponse(
        appTitle=settings.app_title,
        endpoints={
            "openAI": {
                "availableModels": ["gpt-4", "gpt-3.5-turbo"],
                "userProvide": False,
            },
            "anthropic": {
                "availableModels": ["claude-3-opus", "claude-3-sonnet"],
                "userProvide": False,
            },
        },
        modelSpecs={},
        interface={
            "privacyPolicy": {},
            "termsOfService": {},
        },
    )

    return config
