"""Project model"""
from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from bson import ObjectId


class Project(Document):
    """Project document model"""
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(default=None, description="Project description")
    owner: ObjectId = Field(..., description="Owner user ID")

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "projects"
        indexes = [
            IndexModel([("owner", ASCENDING)]),
        ]
