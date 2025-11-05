"""
Conversation request/response schemas.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""
    conversationId: Optional[str] = Field(None, description="Conversation ID")
    title: str = Field(..., min_length=1, max_length=200, description="Conversation title")
    endpoint: Optional[str] = Field(None, description="AI endpoint")
    model: Optional[str] = Field(None, description="AI model")
    agentOptions: Optional[Dict[str, Any]] = Field(None, description="Agent configuration")
    modelLabel: Optional[str] = Field(None, description="Model display label")
    iconURL: Optional[str] = Field(None, description="Icon URL")


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""
    conversationId: str = Field(..., description="Conversation ID")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Title")
    endpoint: Optional[str] = Field(None, description="AI endpoint")
    model: Optional[str] = Field(None, description="AI model")
    agentOptions: Optional[Dict[str, Any]] = Field(None, description="Agent configuration")
    isArchived: Optional[bool] = Field(None, description="Archive status")
    tags: Optional[List[str]] = Field(None, description="Tags")


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    conversationId: str
    title: str
    endpoint: Optional[str] = None
    model: Optional[str] = None
    agentOptions: Optional[Dict[str, Any]] = None
    modelLabel: Optional[str] = None
    iconURL: Optional[str] = None
    isArchived: bool = False
    tags: List[str] = []
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class ConversationsListResponse(BaseModel):
    """Schema for paginated conversations list."""
    conversations: List[ConversationResponse]
    pageNumber: int
    pageSize: int
    pages: int


class DeleteConversationRequest(BaseModel):
    """Schema for deleting conversations."""
    conversationId: Optional[str] = Field(None, description="Specific conversation ID")
    source: Optional[str] = Field(None, description="Deletion source")
    thread_id: Optional[str] = Field(None, description="OpenAI thread ID")
    endpoint: Optional[str] = Field(None, description="Endpoint for thread cleanup")


class ForkConversationRequest(BaseModel):
    """Schema for forking a conversation."""
    conversationId: str = Field(..., description="Source conversation ID")
    messageId: str = Field(..., description="Target message ID to fork from")
    option: Optional[str] = Field(None, description="Fork option (branch/direct)")
    splitAtTarget: bool = Field(False, description="Split at target message")
    latestMessageId: Optional[str] = Field(None, description="Latest message ID")


class ForkConversationResponse(BaseModel):
    """Schema for fork response."""
    conversationId: str = Field(..., description="New conversation ID")
    title: str = Field(..., description="New conversation title")
    messages: List[str] = Field(..., description="Message IDs in forked conversation")


class DuplicateConversationRequest(BaseModel):
    """Schema for duplicating a conversation."""
    conversationId: str = Field(..., description="Source conversation ID")
    title: Optional[str] = Field(None, description="New conversation title")


class GenerateTitleRequest(BaseModel):
    """Schema for generating conversation title."""
    conversationId: str = Field(..., description="Conversation ID")


class GenerateTitleResponse(BaseModel):
    """Schema for generated title response."""
    title: str = Field(..., description="Generated title")
