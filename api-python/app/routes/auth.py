"""Authentication routes"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.models import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    TwoFactorVerifyRequest,
    TwoFactorEnableResponse,
)
from app.schemas.user import UserResponse
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    create_password_reset_token,
    verify_password_reset_token,
)
from app.utils.totp import (
    generate_totp_secret,
    generate_totp_qr_code,
    verify_totp_code,
    generate_backup_codes,
)
from app.utils.exceptions import (
    AuthenticationError,
    ValidationError,
    ConflictError,
    NotFoundError,
)
from app.utils.logger import logger
from app.middleware import get_current_user, get_current_active_user
from app.config import get_settings


router = APIRouter()
settings = get_settings()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """
    Register a new user

    Args:
        request: Registration request

    Returns:
        Created user

    Raises:
        ConflictError: If email already exists
        ValidationError: If validation fails
    """
    # Check if registration is allowed
    if not settings.allow_registration:
        raise ValidationError("Registration is currently disabled")

    # Check if user already exists
    existing_user = await User.find_one({"email": request.email})
    if existing_user:
        raise ConflictError("Email already registered")

    # Create new user
    user = User(
        name=request.name,
        username=request.username or request.email.split("@")[0],
        email=request.email,
        password=hash_password(request.password),
        provider="local",
        role="USER",
        email_verified=not settings.allow_email_verification,  # Auto-verify if not required
    )

    await user.insert()
    logger.info(f"New user registered: {user.email}")

    return UserResponse.model_validate(user)


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login with email and password

    Args:
        request: Login request

    Returns:
        Login response with user and tokens

    Raises:
        AuthenticationError: If credentials are invalid
    """
    # Find user by email
    user = await User.find_one({"email": request.email})
    if not user or not user.password:
        raise AuthenticationError("Invalid email or password")

    # Verify password
    if not verify_password(request.password, user.password):
        raise AuthenticationError("Invalid email or password")

    # Check if 2FA is enabled
    if user.two_factor_enabled:
        # Return temporary token for 2FA verification
        # In a real implementation, you'd store this in Redis with short expiry
        temp_token = create_access_token(
            data={"sub": str(user.id), "temp": True},
            expires_delta=timedelta(minutes=5)
        )
        raise AuthenticationError(
            "2FA required",
            details={"requires_2fa": True, "temp_token": temp_token}
        )

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Update last login (optional)
    user.updated_at = datetime.utcnow()
    await user.save()

    logger.info(f"User logged in: {user.email}")

    return LoginResponse(
        user=UserResponse.model_validate(user).model_dump(),
        token=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_expiration
        )
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout current user

    Args:
        current_user: Current authenticated user

    Returns:
        Success message
    """
    # In a real implementation, you'd invalidate the token
    # by adding it to a Redis blacklist or removing from session storage
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token

    Args:
        request: Refresh token request

    Returns:
        New token response

    Raises:
        AuthenticationError: If refresh token is invalid
    """
    # Decode refresh token
    payload = decode_token(request.refresh_token, token_type="refresh")
    if not payload:
        raise AuthenticationError("Invalid or expired refresh token")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")

    # Verify user exists
    user = await User.find_one({"_id": user_id})
    if not user:
        raise AuthenticationError("User not found")

    # Create new tokens
    access_token = create_access_token(data={"sub": user_id})
    refresh_token = create_refresh_token(data={"sub": user_id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_expiration
    )


@router.post("/request-password-reset")
async def request_password_reset(request: PasswordResetRequest):
    """
    Request password reset email

    Args:
        request: Password reset request

    Returns:
        Success message
    """
    # Find user
    user = await User.find_one({"email": request.email})
    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a reset link has been sent"}

    # Generate reset token
    reset_token = create_password_reset_token(user.email)

    # In a real implementation, send email with reset link
    # For now, just log it
    logger.info(f"Password reset requested for: {user.email}")
    logger.debug(f"Reset token: {reset_token}")

    # TODO: Send email with reset link
    # reset_link = f"http://localhost:3080/reset-password?token={reset_token}"
    # await send_password_reset_email(user.email, reset_link)

    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(request: PasswordResetConfirm):
    """
    Reset password using reset token

    Args:
        request: Password reset confirmation

    Returns:
        Success message

    Raises:
        AuthenticationError: If token is invalid
    """
    # Verify token
    email = verify_password_reset_token(request.token)
    if not email:
        raise AuthenticationError("Invalid or expired reset token")

    # Find user
    user = await User.find_one({"email": email})
    if not user:
        raise NotFoundError("User not found")

    # Update password
    user.password = hash_password(request.password)
    user.updated_at = datetime.utcnow()
    await user.save()

    logger.info(f"Password reset for: {user.email}")

    return {"message": "Password has been reset successfully"}


# 2FA Endpoints


@router.get("/2fa/enable", response_model=TwoFactorEnableResponse)
async def enable_2fa(current_user: User = Depends(get_current_active_user)):
    """
    Enable 2FA for current user

    Args:
        current_user: Current authenticated user

    Returns:
        2FA setup information with QR code

    Raises:
        ValidationError: If 2FA is already enabled
    """
    if current_user.two_factor_enabled:
        raise ValidationError("2FA is already enabled")

    # Generate TOTP secret
    secret = generate_totp_secret()

    # Generate QR code
    qr_code = generate_totp_qr_code(secret, current_user.email)

    # Generate backup codes
    backup_codes, hashed_codes = generate_backup_codes()

    # Store secret and backup codes (but don't enable 2FA yet)
    # User needs to verify the code first
    current_user.totp_secret = secret
    current_user.backup_codes = hashed_codes
    await current_user.save()

    return TwoFactorEnableResponse(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes
    )


@router.post("/2fa/verify")
async def verify_2fa(
    request: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Verify 2FA code to complete login

    Args:
        request: 2FA verification request
        current_user: Current authenticated user

    Returns:
        Login response with tokens

    Raises:
        AuthenticationError: If code is invalid
    """
    if not current_user.totp_secret:
        raise AuthenticationError("2FA is not set up")

    # Verify code
    if not verify_totp_code(current_user.totp_secret, request.code):
        raise AuthenticationError("Invalid 2FA code")

    # Create tokens
    access_token = create_access_token(data={"sub": str(current_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(current_user.id)})

    return LoginResponse(
        user=UserResponse.model_validate(current_user).model_dump(),
        token=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_expiration
        )
    )


@router.post("/2fa/confirm")
async def confirm_2fa(
    request: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Confirm 2FA setup and enable it

    Args:
        request: 2FA verification request
        current_user: Current authenticated user

    Returns:
        Success message

    Raises:
        AuthenticationError: If code is invalid
    """
    if not current_user.totp_secret:
        raise AuthenticationError("2FA is not set up")

    # Verify code
    if not verify_totp_code(current_user.totp_secret, request.code):
        raise AuthenticationError("Invalid 2FA code")

    # Enable 2FA
    current_user.two_factor_enabled = True
    await current_user.save()

    logger.info(f"2FA enabled for: {current_user.email}")

    return {"message": "2FA has been enabled successfully"}


@router.post("/2fa/disable")
async def disable_2fa(
    request: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Disable 2FA for current user

    Args:
        request: 2FA verification request
        current_user: Current authenticated user

    Returns:
        Success message

    Raises:
        AuthenticationError: If code is invalid
        ValidationError: If 2FA is not enabled
    """
    if not current_user.two_factor_enabled:
        raise ValidationError("2FA is not enabled")

    # Verify code
    if not verify_totp_code(current_user.totp_secret, request.code):
        raise AuthenticationError("Invalid 2FA code")

    # Disable 2FA
    current_user.two_factor_enabled = False
    current_user.totp_secret = None
    current_user.backup_codes = []
    await current_user.save()

    logger.info(f"2FA disabled for: {current_user.email}")

    return {"message": "2FA has been disabled successfully"}
