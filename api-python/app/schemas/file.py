"""
File request/response schemas.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """Schema for file upload response."""
    file_id: str = Field(..., description="File ID")
    filename: str = Field(..., description="Filename")
    filepath: str = Field(..., description="File path")
    bytes: int = Field(..., description="File size in bytes")
    type: str = Field(..., description="MIME type")
    width: Optional[int] = Field(None, description="Image width")
    height: Optional[int] = Field(None, description="Image height")
    source: str = Field(..., description="File source (local, s3, etc.)")


class FileResponse(BaseModel):
    """Schema for file response."""
    file_id: str
    filename: str
    filepath: str
    bytes: int
    type: str
    width: Optional[int] = None
    height: Optional[int] = None
    source: str
    user: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class DeleteFilesRequest(BaseModel):
    """Schema for deleting files."""
    files: List[dict] = Field(..., description="List of files to delete")
    agent_id: Optional[str] = Field(None, description="Agent ID for permission check")
    assistant_id: Optional[str] = Field(None, description="Assistant ID for permission check")
    tool_resource: Optional[str] = Field(None, description="Tool resource type")


class FileConfigResponse(BaseModel):
    """Schema for file configuration."""
    endpoints: dict = Field(..., description="Endpoint file configurations")
    serverFileSizeLimit: int = Field(..., description="Max file size in bytes")
    avatarSizeLimit: int = Field(..., description="Max avatar size in bytes")
