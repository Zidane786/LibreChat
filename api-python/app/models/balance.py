"""Balance model (for user token balances)"""
from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from bson import ObjectId


class Balance(Document):
    """Balance document model"""
    user: ObjectId = Field(..., description="User ID")
    token_credits: float = Field(default=0.0, description="Available token credits")
    spent_credits: float = Field(default=0.0, description="Spent token credits")

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "balances"
        indexes = [
            IndexModel([("user", ASCENDING)], unique=True),
        ]
