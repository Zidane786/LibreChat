"""Authentication request/response schemas"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, max_length=128, description="User password")


class RegisterRequest(BaseModel):
    """Registration request schema"""
    name: Optional[str] = Field(default=None, description="User's name")
    username: Optional[str] = Field(default=None, description="Username")
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    confirm_password: str = Field(..., min_length=8, max_length=128, description="Password confirmation")

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        """Validate that passwords match"""
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str = Field(..., description="JWT refresh token")


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""
    email: EmailStr = Field(..., description="User email")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str = Field(..., description="Reset token")
    password: str = Field(..., min_length=8, max_length=128, description="New password")
    confirm_password: str = Field(..., min_length=8, max_length=128, description="Password confirmation")

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        """Validate that passwords match"""
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class LoginResponse(BaseModel):
    """Login response schema"""
    user: dict = Field(..., description="User information")
    token: TokenResponse = Field(..., description="Authentication tokens")


class TwoFactorVerifyRequest(BaseModel):
    """2FA verification request schema"""
    code: str = Field(..., min_length=6, max_length=6, description="TOTP code")


class TwoFactorEnableResponse(BaseModel):
    """2FA enable response schema"""
    secret: str = Field(..., description="TOTP secret")
    qr_code: str = Field(..., description="QR code data URL")
    backup_codes: list[str] = Field(..., description="Backup codes")
