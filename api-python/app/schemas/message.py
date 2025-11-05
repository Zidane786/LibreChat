"""
Message request/response schemas.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ContentPart(BaseModel):
    """Content part within a message."""
    type: str = Field(..., description="Content type (text, image_url, tool_call, etc.)")
    text: Optional[str] = Field(None, description="Text content")
    image_url: Optional[Dict[str, Any]] = Field(None, description="Image URL data")
    tool_call: Optional[Dict[str, Any]] = Field(None, description="Tool call data")


class MessageCreate(BaseModel):
    """Schema for creating a new message."""
    conversationId: str = Field(..., description="Conversation ID")
    messageId: Optional[str] = Field(None, description="Message ID (generated if not provided)")
    parentMessageId: Optional[str] = Field(None, description="Parent message ID for threading")
    text: Optional[str] = Field(None, description="Message text content")
    content: Optional[List[ContentPart]] = Field(None, description="Structured content parts")
    endpoint: Optional[str] = Field(None, description="AI endpoint used")
    model: Optional[str] = Field(None, description="AI model used")
    isCreatedByUser: bool = Field(True, description="Whether message is from user")
    error: Optional[bool] = Field(None, description="Whether message contains error")
    unfinished: Optional[bool] = Field(None, description="Whether message is incomplete")
    tokenCount: Optional[int] = Field(None, description="Token count")


class MessageUpdate(BaseModel):
    """Schema for updating a message."""
    text: Optional[str] = Field(None, description="Updated text")
    content: Optional[List[ContentPart]] = Field(None, description="Updated content")
    index: Optional[int] = Field(None, description="Content part index to update")
    model: Optional[str] = Field(None, description="Model for token counting")
    tokenCount: Optional[int] = Field(None, description="Updated token count")


class MessageFeedback(BaseModel):
    """Schema for message feedback."""
    feedback: Optional[str] = Field(None, description="Feedback value (thumbs up/down, etc.)")


class ArtifactUpdate(BaseModel):
    """Schema for updating artifact content."""
    index: int = Field(..., ge=0, description="Artifact index")
    original: str = Field(..., description="Original content to replace")
    updated: str = Field(..., description="Updated content")


class MessageResponse(BaseModel):
    """Schema for message response."""
    messageId: str
    conversationId: str
    parentMessageId: Optional[str] = None
    text: Optional[str] = None
    content: Optional[List[ContentPart]] = None
    endpoint: Optional[str] = None
    model: Optional[str] = None
    isCreatedByUser: bool
    error: Optional[bool] = None
    unfinished: Optional[bool] = None
    tokenCount: Optional[int] = None
    feedback: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class MessagesListResponse(BaseModel):
    """Schema for paginated messages list."""
    messages: List[MessageResponse]
    nextCursor: Optional[str] = None


class MessageSearchResult(BaseModel):
    """Schema for message search results."""
    messageId: str
    conversationId: str
    text: Optional[str] = None
    content: Optional[List[ContentPart]] = None
    title: Optional[str] = Field(None, description="Conversation title")
    model: Optional[str] = None
    endpoint: Optional[str] = None
    isCreatedByUser: Optional[bool] = None
    iconURL: Optional[str] = None
    createdAt: datetime

    class Config:
        from_attributes = True
