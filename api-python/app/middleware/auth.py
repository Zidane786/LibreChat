"""Authentication middleware and dependencies"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models import User
from app.utils.auth import decode_token
from app.utils.exceptions import AuthenticationError, AuthorizationError


# HTTP Bearer security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get current authenticated user from JWT token

    Args:
        credentials: HTTP authorization credentials

    Returns:
        Current user

    Raises:
        AuthenticationError: If token is invalid or user not found
    """
    token = credentials.credentials

    # Decode token
    payload = decode_token(token, token_type="access")
    if not payload:
        raise AuthenticationError("Invalid or expired token")

    # Get user ID from payload
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")

    # Fetch user from database
    user = await User.find_one({"_id": user_id})
    if not user:
        raise AuthenticationError("User not found")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (verified email if required)

    Args:
        current_user: Current authenticated user

    Returns:
        Current active user

    Raises:
        AuthenticationError: If user is not active
    """
    from app.config import get_settings
    settings = get_settings()

    # Check email verification if enabled
    if settings.allow_email_verification and not current_user.email_verified:
        raise AuthenticationError("Email not verified")

    return current_user


def require_role(*allowed_roles: str):
    """
    Dependency to require specific user roles

    Args:
        *allowed_roles: Allowed role names

    Returns:
        Dependency function
    """
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        """Check if user has required role"""
        if current_user.role not in allowed_roles:
            raise AuthorizationError(
                f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user

    return role_checker


async def optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise None

    Args:
        credentials: Optional HTTP authorization credentials

    Returns:
        Current user or None
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except (AuthenticationError, HTTPException):
        return None
