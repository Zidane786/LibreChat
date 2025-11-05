"""ToolCall model (for tracking agent tool invocations)"""
from datetime import datetime
from typing import Optional, Dict, Any
from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from bson import ObjectId


class ToolCall(Document):
    """Tool call document model"""
    user: ObjectId = Field(..., description="User ID")
    conversation_id: str = Field(..., description="Conversation ID")
    message_id: str = Field(..., description="Message ID")
    tool_call_id: str = Field(..., description="Tool call ID")

    # Tool information
    tool_name: str = Field(..., description="Tool name")
    tool_input: Optional[Dict[str, Any]] = Field(default=None, description="Tool input")
    tool_output: Optional[Dict[str, Any]] = Field(default=None, description="Tool output")

    # Status
    status: str = Field(default="pending", description="Tool call status")
    error: Optional[str] = Field(default=None, description="Error message if failed")

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "tool_calls"
        indexes = [
            IndexModel([("tool_call_id", ASCENDING)], unique=True),
            IndexModel([("user", ASCENDING)]),
            IndexModel([("conversation_id", ASCENDING)]),
            IndexModel([("message_id", ASCENDING)]),
        ]
