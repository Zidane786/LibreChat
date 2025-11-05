"""Prompt and PromptGroup models"""
from datetime import datetime
from typing import Optional, List
from enum import Enum
from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from bson import ObjectId


class PromptType(str, Enum):
    """Prompt type enum"""
    TEXT = "text"
    CHAT = "chat"


class Prompt(Document):
    """Prompt document model"""
    group_id: ObjectId = Field(..., description="Prompt group ID")
    author: ObjectId = Field(..., description="Author user ID")
    prompt: str = Field(..., description="Prompt text")
    type: PromptType = Field(..., description="Prompt type")

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "prompts"
        indexes = [
            IndexModel([("group_id", ASCENDING)]),
            IndexModel([("author", ASCENDING)]),
            IndexModel([("created_at", ASCENDING), ("updated_at", ASCENDING)]),
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "You are a helpful assistant",
                "type": "text"
            }
        }


class PromptGroup(Document):
    """Prompt group document model"""
    name: str = Field(..., description="Group name")
    author: ObjectId = Field(..., description="Author user ID")
    author_name: Optional[str] = Field(default=None, description="Author name")
    description: Optional[str] = Field(default=None, description="Group description")
    category: Optional[str] = Field(default="general", description="Category")

    # Production status
    production_id: Optional[ObjectId] = Field(default=None, description="Production version ID")
    is_production: bool = Field(default=False, description="Is production version")

    # Project association
    project_ids: Optional[List[ObjectId]] = Field(default=None, description="Associated project IDs")

    # Versioning
    versions: List = Field(default_factory=list, description="Version history")

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "prompt_groups"
        indexes = [
            IndexModel([("author", ASCENDING)]),
            IndexModel([("project_ids", ASCENDING)]),
            IndexModel([("created_at", ASCENDING), ("updated_at", ASCENDING)]),
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "My Prompts",
                "description": "Collection of useful prompts",
                "category": "general"
            }
        }
