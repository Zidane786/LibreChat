"""
Balance routes for token tracking.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from app.models.balance import Balance
from app.models.user import User
from app.middleware.auth import get_current_active_user
from app.utils.logger import logger

router = APIRouter(prefix="/api/balance", tags=["balance"])


class BalanceResponse(BaseModel):
    """Schema for balance response."""
    balance: int
    tokenCredits: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=BalanceResponse)
async def get_balance(
    current_user: User = Depends(get_current_active_user),
):
    """Get user's token balance."""
    try:
        balance = await Balance.find_one(Balance.user == current_user.id)

        if not balance:
            # Create default balance
            balance = Balance(user=current_user.id, balance=0, tokenCredits=0)
            await balance.insert()

        return BalanceResponse(**balance.dict())

    except Exception as e:
        logger.error(f"Error fetching balance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching balance",
        )
