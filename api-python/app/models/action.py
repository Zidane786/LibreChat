"""Action model (for custom actions)"""
from datetime import datetime
from typing import Optional, Dict, Any
from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from bson import ObjectId


class Action(Document):
    """Action document model"""
    id: str = Field(..., description="Unique action ID")
    name: str = Field(..., description="Action name")
    description: Optional[str] = Field(default=None, description="Action description")
    author: ObjectId = Field(..., description="Author user ID")

    # Action configuration
    action_type: str = Field(..., description="Action type")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Action metadata")

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "actions"
        indexes = [
            IndexModel([("id", ASCENDING)], unique=True),
            IndexModel([("author", ASCENDING)]),
        ]
