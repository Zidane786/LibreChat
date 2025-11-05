"""User model"""
from datetime import datetime
from typing import Optional, List
from beanie import Document
from pydantic import BaseModel, Field, EmailStr
from pymongo import IndexModel, ASCENDING


class Session(BaseModel):
    """User session sub-document"""
    refresh_token: str = Field(default="", description="Refresh token")


class BackupCode(BaseModel):
    """2FA backup code sub-document"""
    code_hash: str = Field(..., description="Hashed backup code")
    used: bool = Field(default=False, description="Whether code has been used")
    used_at: Optional[datetime] = Field(default=None, description="When code was used")


class Personalization(BaseModel):
    """User personalization settings"""
    memories: bool = Field(default=True, description="Enable memories")


class User(Document):
    """User document model"""
    name: Optional[str] = Field(default=None, description="User's name")
    username: str = Field(default="", description="Username")
    email: EmailStr = Field(..., description="User's email address")
    email_verified: bool = Field(default=False, description="Email verification status")
    password: Optional[str] = Field(default=None, description="Hashed password", exclude=True)
    avatar: Optional[str] = Field(default=None, description="Avatar URL")
    provider: str = Field(default="local", description="Authentication provider")
    role: str = Field(default="USER", description="User role")

    # OAuth provider IDs
    google_id: Optional[str] = Field(default=None, description="Google OAuth ID")
    facebook_id: Optional[str] = Field(default=None, description="Facebook OAuth ID")
    openid_id: Optional[str] = Field(default=None, description="OpenID Connect ID")
    saml_id: Optional[str] = Field(default=None, description="SAML ID")
    ldap_id: Optional[str] = Field(default=None, description="LDAP ID")
    github_id: Optional[str] = Field(default=None, description="GitHub OAuth ID")
    discord_id: Optional[str] = Field(default=None, description="Discord OAuth ID")
    apple_id: Optional[str] = Field(default=None, description="Apple OAuth ID")

    # Plugin and settings
    plugins: List = Field(default_factory=list, description="Enabled plugins")

    # Two-Factor Authentication
    two_factor_enabled: bool = Field(default=False, description="2FA enabled status")
    totp_secret: Optional[str] = Field(default=None, description="TOTP secret", exclude=True)
    backup_codes: List[BackupCode] = Field(default_factory=list, description="Backup codes", exclude=True)

    # Session management
    refresh_token: List[Session] = Field(default_factory=list, description="Active sessions")

    # Account expiry (for temporary accounts)
    expires_at: Optional[datetime] = Field(default=None, description="Account expiration")

    # Terms acceptance
    terms_accepted: bool = Field(default=False, description="Terms of service accepted")

    # Personalization
    personalization: Personalization = Field(default_factory=Personalization, description="User preferences")

    # External source identification
    id_on_the_source: Optional[str] = Field(default=None, description="External source ID")

    # Timestamps (handled by Beanie)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        indexes = [
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("google_id", ASCENDING)], unique=True, sparse=True),
            IndexModel([("facebook_id", ASCENDING)], unique=True, sparse=True),
            IndexModel([("openid_id", ASCENDING)], unique=True, sparse=True),
            IndexModel([("saml_id", ASCENDING)], unique=True, sparse=True),
            IndexModel([("ldap_id", ASCENDING)], unique=True, sparse=True),
            IndexModel([("github_id", ASCENDING)], unique=True, sparse=True),
            IndexModel([("discord_id", ASCENDING)], unique=True, sparse=True),
            IndexModel([("apple_id", ASCENDING)], unique=True, sparse=True),
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "provider": "local",
                "role": "USER"
            }
        }
