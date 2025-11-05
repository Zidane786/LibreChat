"""Message model"""
from datetime import datetime
from typing import Optional, List, Any, Dict
from enum import Enum
from beanie import Document
from pydantic import BaseModel, Field
from pymongo import IndexModel, ASCENDING


class FeedbackRating(str, Enum):
    """Message feedback rating enum"""
    THUMBS_UP = "thumbsUp"
    THUMBS_DOWN = "thumbsDown"


class MessageFeedback(BaseModel):
    """Message feedback sub-document"""
    rating: FeedbackRating = Field(..., description="Feedback rating")
    tag: Optional[Any] = Field(default=None, description="Feedback tag")
    text: Optional[str] = Field(default=None, description="Feedback text")


class Message(Document):
    """Message document model"""
    message_id: str = Field(..., description="Unique message ID")
    conversation_id: str = Field(..., description="Conversation ID")
    user: str = Field(..., description="User ID")

    # Message content
    text: Optional[str] = Field(default=None, description="Message text")
    sender: Optional[str] = Field(default=None, description="Sender identifier")
    is_created_by_user: bool = Field(default=False, description="Message from user")

    # Model and endpoint
    model: Optional[str] = Field(default=None, description="Model used")
    endpoint: Optional[str] = Field(default=None, description="Endpoint used")

    # Thread information
    parent_message_id: Optional[str] = Field(default=None, description="Parent message ID")
    thread_id: Optional[str] = Field(default=None, description="Thread ID for assistants")

    # Token tracking
    token_count: Optional[int] = Field(default=None, description="Token count")
    summary_token_count: Optional[int] = Field(default=None, description="Summary token count")

    # Message metadata
    conversation_signature: Optional[str] = Field(default=None, description="Conversation signature")
    client_id: Optional[str] = Field(default=None, description="Client ID")
    invocation_id: Optional[int] = Field(default=None, description="Invocation ID")
    summary: Optional[str] = Field(default=None, description="Message summary")

    # Status flags
    unfinished: bool = Field(default=False, description="Message incomplete")
    error: bool = Field(default=False, description="Message has error")
    finish_reason: Optional[str] = Field(default=None, description="Completion finish reason")

    # Feedback
    feedback: Optional[MessageFeedback] = Field(default=None, description="User feedback")

    # Files and attachments
    files: Optional[List[Dict[str, Any]]] = Field(default=None, description="Attached files")
    attachments: Optional[List[Dict[str, Any]]] = Field(default=None, description="Attachments")

    # Plugin information
    plugin: Optional[Dict[str, Any]] = Field(default=None, description="Plugin data")
    plugins: Optional[List[Dict[str, Any]]] = Field(default=None, description="Plugins used")

    # Content (for multi-part messages)
    content: Optional[List[Dict[str, Any]]] = Field(default=None, description="Message content parts")

    # Frontend components
    icon_url: Optional[str] = Field(default=None, description="Icon URL")

    # Meilisearch indexing
    _meili_index: bool = Field(default=False, description="Meilisearch indexed", exclude=True)

    # Expiration
    expired_at: Optional[datetime] = Field(default=None, description="Message expiration")

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "messages"
        indexes = [
            IndexModel([("message_id", ASCENDING)], unique=True),
            IndexModel([("conversation_id", ASCENDING)]),
            IndexModel([("user", ASCENDING)]),
            IndexModel([("message_id", ASCENDING), ("user", ASCENDING)], unique=True),
            IndexModel([("created_at", ASCENDING)]),
            IndexModel([("expired_at", ASCENDING)], expireAfterSeconds=0),
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "msg-123",
                "conversation_id": "conv-123",
                "user": "user-123",
                "text": "Hello, how can I help?",
                "sender": "user",
                "is_created_by_user": True
            }
        }
