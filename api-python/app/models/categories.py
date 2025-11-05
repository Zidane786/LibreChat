"""Categories model"""
from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING


class Categories(Document):
    """Categories document model"""
    name: str = Field(..., description="Category name")
    type: str = Field(..., description="Category type (agent, prompt, etc.)")
    description: Optional[str] = Field(default=None, description="Category description")
    position: int = Field(default=0, description="Display position")

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "categories"
        indexes = [
            IndexModel([("type", ASCENDING)]),
            IndexModel([("name", ASCENDING), ("type", ASCENDING)], unique=True),
        ]
