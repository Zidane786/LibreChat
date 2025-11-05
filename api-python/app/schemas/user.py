"""User request/response schemas"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    """User response schema"""
    id: str = Field(..., description="User ID")
    name: Optional[str] = Field(default=None, description="User's name")
    username: str = Field(..., description="Username")
    email: EmailStr = Field(..., description="User email")
    email_verified: bool = Field(..., description="Email verification status")
    avatar: Optional[str] = Field(default=None, description="Avatar URL")
    provider: str = Field(..., description="Authentication provider")
    role: str = Field(..., description="User role")
    two_factor_enabled: bool = Field(..., description="2FA status")
    terms_accepted: bool = Field(..., description="Terms acceptance status")
    created_at: datetime = Field(..., description="Account creation date")
    updated_at: datetime = Field(..., description="Last update date")

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User update schema"""
    name: Optional[str] = Field(default=None, description="User's name")
    username: Optional[str] = Field(default=None, description="Username")
    avatar: Optional[str] = Field(default=None, description="Avatar URL")


class AcceptTermsRequest(BaseModel):
    """Accept terms request schema"""
    accepted: bool = Field(..., description="Terms accepted")
