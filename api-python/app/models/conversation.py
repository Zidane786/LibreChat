"""Conversation model"""
from datetime import datetime
from typing import Optional, List, Any, Dict
from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING, DESCENDING
from bson import ObjectId


class Conversation(Document):
    """Conversation document model"""
    conversation_id: str = Field(..., description="Unique conversation ID")
    title: str = Field(default="New Chat", description="Conversation title")
    user: str = Field(..., description="User ID who owns this conversation")
    messages: List[ObjectId] = Field(default_factory=list, description="Message references")

    # Agent and model configuration
    agent_options: Optional[Dict[str, Any]] = Field(default=None, description="Agent options")
    agent_id: Optional[str] = Field(default=None, description="Agent ID")
    endpoint: Optional[str] = Field(default=None, description="Endpoint")
    model: Optional[str] = Field(default=None, description="Model name")
    model_label: Optional[str] = Field(default=None, description="Model label")

    # Assistant configuration
    assistant_id: Optional[str] = Field(default=None, description="Assistant ID")

    # Additional metadata
    tags: List[str] = Field(default_factory=list, description="Conversation tags")
    files: List[str] = Field(default_factory=list, description="Attached file IDs")
    is_archived: Optional[bool] = Field(default=False, description="Archive status")

    # Expiration
    expired_at: Optional[datetime] = Field(default=None, description="Expiration date for temporary chats")

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "conversations"
        indexes = [
            IndexModel([("conversation_id", ASCENDING)], unique=True),
            IndexModel([("user", ASCENDING)]),
            IndexModel([("conversation_id", ASCENDING), ("user", ASCENDING)], unique=True),
            IndexModel([("created_at", ASCENDING), ("updated_at", ASCENDING)]),
            IndexModel([("expired_at", ASCENDING)], expireAfterSeconds=0),
            IndexModel([("updated_at", DESCENDING)]),
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "abc-123",
                "title": "New Chat",
                "user": "user-id-123",
                "endpoint": "openai",
                "model": "gpt-4"
            }
        }
