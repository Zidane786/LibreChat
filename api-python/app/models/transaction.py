"""Transaction model (for token/balance transactions)"""
from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from bson import ObjectId


class Transaction(Document):
    """Transaction document model"""
    user: ObjectId = Field(..., description="User ID")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID")
    model: Optional[str] = Field(default=None, description="Model used")
    context: Optional[str] = Field(default=None, description="Transaction context")

    # Token usage
    raw_amount: int = Field(..., description="Raw token amount")
    token_credits: float = Field(..., description="Token credits")
    rate: float = Field(..., description="Rate used for conversion")

    # Transaction type
    transaction_type: str = Field(..., description="Transaction type (debit/credit)")

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "transactions"
        indexes = [
            IndexModel([("user", ASCENDING)]),
            IndexModel([("conversation_id", ASCENDING)]),
            IndexModel([("created_at", ASCENDING)]),
        ]
