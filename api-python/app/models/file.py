"""File model"""
from datetime import datetime
from typing import Optional, Dict
from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from bson import ObjectId


class File(Document):
    """File document model"""
    user: ObjectId = Field(..., description="User ID (ObjectId reference)")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID")
    file_id: str = Field(..., description="Unique file ID")
    temp_file_id: Optional[str] = Field(default=None, description="Temporary file ID")

    # File metadata
    bytes: int = Field(..., description="File size in bytes")
    filename: str = Field(..., description="Original filename")
    filepath: str = Field(..., description="Storage filepath or URL")
    object: str = Field(default="file", description="Object type")
    type: str = Field(..., description="MIME type")

    # File processing
    embedded: Optional[bool] = Field(default=None, description="File is embedded for vector search")
    text: Optional[str] = Field(default=None, description="Extracted text content")
    context: Optional[str] = Field(default=None, description="File context (e.g., 'agents')")

    # Usage tracking
    usage: int = Field(default=0, description="Usage count")

    # Storage source
    source: str = Field(default="local", description="Storage source (local, s3, azure)")

    # AI model association
    model: Optional[str] = Field(default=None, description="Associated model")

    # Image dimensions
    width: Optional[int] = Field(default=None, description="Image width")
    height: Optional[int] = Field(default=None, description="Image height")

    # Additional metadata
    metadata: Optional[Dict[str, str]] = Field(default=None, description="Additional metadata")

    # Expiration (TTL)
    expires_at: Optional[datetime] = Field(default=None, description="Expiration timestamp")

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "files"
        indexes = [
            IndexModel([("file_id", ASCENDING)]),
            IndexModel([("user", ASCENDING)]),
            IndexModel([("conversation_id", ASCENDING)]),
            IndexModel([("created_at", ASCENDING), ("updated_at", ASCENDING)]),
            IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=3600),  # 1 hour
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "file-123",
                "filename": "document.pdf",
                "filepath": "/uploads/document.pdf",
                "bytes": 102400,
                "type": "application/pdf",
                "source": "local"
            }
        }
