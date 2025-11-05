"""Banner model (for system announcements)"""
from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING


class Banner(Document):
    """Banner document model"""
    type: str = Field(..., description="Banner type (info, warning, error)")
    title: str = Field(..., description="Banner title")
    message: str = Field(..., description="Banner message")
    active: bool = Field(default=True, description="Is active")

    # Timestamps
    start_date: Optional[datetime] = Field(default=None, description="Start date")
    end_date: Optional[datetime] = Field(default=None, description="End date")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "banners"
        indexes = [
            IndexModel([("active", ASCENDING)]),
        ]
