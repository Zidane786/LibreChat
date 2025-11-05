"""Assistant model (for OpenAI/Azure assistants)"""
from datetime import datetime
from typing import Optional, Dict, Any
from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from bson import ObjectId


class Assistant(Document):
    """Assistant document model"""
    id: str = Field(..., description="Unique assistant ID")
    user: ObjectId = Field(..., description="User ID")
    object: str = Field(default="assistant", description="Object type")
    name: Optional[str] = Field(default=None, description="Assistant name")
    description: Optional[str] = Field(default=None, description="Assistant description")
    model: str = Field(..., description="Model name")
    instructions: Optional[str] = Field(default=None, description="Assistant instructions")

    # Configuration
    tools: Optional[Dict[str, Any]] = Field(default=None, description="Enabled tools")
    file_ids: Optional[list] = Field(default=None, description="Attached file IDs")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "assistants"
        indexes = [
            IndexModel([("id", ASCENDING)], unique=True),
            IndexModel([("user", ASCENDING)]),
        ]
