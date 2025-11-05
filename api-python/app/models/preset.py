"""Preset model (for conversation presets/templates)"""
from datetime import datetime
from typing import Optional, Dict, Any
from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from bson import ObjectId


class Preset(Document):
    """Preset document model"""
    preset_id: str = Field(..., description="Unique preset ID")
    user: ObjectId = Field(..., description="User ID")
    title: str = Field(..., description="Preset title")

    # Model configuration
    endpoint: Optional[str] = Field(default=None, description="Endpoint")
    model: Optional[str] = Field(default=None, description="Model name")
    model_label: Optional[str] = Field(default=None, description="Model label")

    # Parameters
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Model parameters")

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "presets"
        indexes = [
            IndexModel([("preset_id", ASCENDING)], unique=True),
            IndexModel([("user", ASCENDING)]),
        ]
