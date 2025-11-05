"""ConversationTag model"""
from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from bson import ObjectId


class ConversationTag(Document):
    """Conversation tag document model"""
    user: ObjectId = Field(..., description="User ID")
    tag: str = Field(..., description="Tag name")
    description: Optional[str] = Field(default=None, description="Tag description")
    position: int = Field(default=0, description="Display position")

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "conversation_tags"
        indexes = [
            IndexModel([("user", ASCENDING)]),
            IndexModel([("tag", ASCENDING)]),
            IndexModel([("user", ASCENDING), ("tag", ASCENDING)], unique=True),
        ]
