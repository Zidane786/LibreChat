"""User routes"""
from fastapi import APIRouter, Depends, status
from app.models import User
from app.schemas.user import UserResponse, UserUpdate, AcceptTermsRequest
from app.middleware import get_current_user, get_current_active_user
from app.utils.logger import logger


router = APIRouter()


@router.get("/", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """
    Get current user profile

    Args:
        current_user: Current authenticated user

    Returns:
        User profile
    """
    return UserResponse.model_validate(current_user)


@router.put("/", response_model=UserResponse)
async def update_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update current user profile

    Args:
        update_data: Update data
        current_user: Current authenticated user

    Returns:
        Updated user profile
    """
    # Update fields
    if update_data.name is not None:
        current_user.name = update_data.name
    if update_data.username is not None:
        current_user.username = update_data.username
    if update_data.avatar is not None:
        current_user.avatar = update_data.avatar

    await current_user.save()
    logger.info(f"User profile updated: {current_user.email}")

    return UserResponse.model_validate(current_user)


@router.get("/terms")
async def get_terms_status(current_user: User = Depends(get_current_user)):
    """
    Get terms of service acceptance status

    Args:
        current_user: Current authenticated user

    Returns:
        Terms acceptance status
    """
    return {
        "terms_accepted": current_user.terms_accepted
    }


@router.post("/terms/accept")
async def accept_terms(
    request: AcceptTermsRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Accept terms of service

    Args:
        request: Accept terms request
        current_user: Current authenticated user

    Returns:
        Success message
    """
    current_user.terms_accepted = request.accepted
    await current_user.save()

    logger.info(f"User accepted terms: {current_user.email}")

    return {"message": "Terms acceptance status updated"}


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(current_user: User = Depends(get_current_active_user)):
    """
    Delete current user account

    Args:
        current_user: Current authenticated user

    Returns:
        No content

    Raises:
        ValidationError: If account deletion is not allowed
    """
    from app.config import get_settings
    from app.utils.exceptions import ValidationError

    settings = get_settings()
    if not settings.allow_account_deletion:
        raise ValidationError("Account deletion is not allowed")

    # TODO: Delete all user data (conversations, messages, files, etc.)
    # This should be done in a background task or transaction

    await current_user.delete()
    logger.info(f"User account deleted: {current_user.email}")

    return None
