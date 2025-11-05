"""Application settings and configuration"""
from functools import lru_cache
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    # Server Configuration
    host: str = Field(default="localhost", description="Server host")
    port: int = Field(default=3080, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")
    app_title: str = Field(default="LibreChat API", description="Application title")

    # Database Configuration
    mongo_uri: str = Field(..., description="MongoDB connection URI")
    mongo_max_pool_size: int = Field(default=10, description="MongoDB max pool size")
    mongo_min_pool_size: int = Field(default=1, description="MongoDB min pool size")
    mongo_max_idle_time_ms: int = Field(default=60000, description="MongoDB max idle time")
    mongo_wait_queue_timeout_ms: int = Field(default=5000, description="MongoDB wait queue timeout")
    mongo_auto_index: bool = Field(default=True, description="Auto create indexes")
    mongo_auto_create: bool = Field(default=True, description="Auto create collections")

    # Redis Configuration
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_db: int = Field(default=0, description="Redis database")

    # JWT Configuration
    jwt_secret: str = Field(..., description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_refresh_secret: str = Field(..., description="JWT refresh secret")
    jwt_expiration: int = Field(default=900, description="JWT expiration in seconds (15 minutes)")
    jwt_refresh_expiration: int = Field(default=604800, description="JWT refresh expiration in seconds (7 days)")

    # Session Configuration
    session_expiry: int = Field(default=900000, description="Session expiry in ms (15 minutes)")
    refresh_token_expiry: int = Field(default=604800000, description="Refresh token expiry in ms (7 days)")

    # Security
    bcrypt_rounds: int = Field(default=12, description="BCrypt salt rounds")
    allowed_domains: Optional[List[str]] = Field(default=None, description="Allowed email domains")

    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3080", "http://localhost:3000"],
        description="CORS allowed origins"
    )
    cors_credentials: bool = Field(default=True, description="Allow credentials")

    # LDAP Configuration
    ldap_url: Optional[str] = Field(default=None, description="LDAP server URL")
    ldap_user_search_base: Optional[str] = Field(default=None, description="LDAP user search base")
    ldap_bind_dn: Optional[str] = Field(default=None, description="LDAP bind DN")
    ldap_bind_password: Optional[str] = Field(default=None, description="LDAP bind password")

    # OAuth Configuration
    google_client_id: Optional[str] = Field(default=None, description="Google OAuth client ID")
    google_client_secret: Optional[str] = Field(default=None, description="Google OAuth client secret")
    google_callback_url: Optional[str] = Field(default=None, description="Google OAuth callback URL")

    github_client_id: Optional[str] = Field(default=None, description="GitHub OAuth client ID")
    github_client_secret: Optional[str] = Field(default=None, description="GitHub OAuth client secret")
    github_callback_url: Optional[str] = Field(default=None, description="GitHub OAuth callback URL")

    discord_client_id: Optional[str] = Field(default=None, description="Discord OAuth client ID")
    discord_client_secret: Optional[str] = Field(default=None, description="Discord OAuth client secret")
    discord_callback_url: Optional[str] = Field(default=None, description="Discord OAuth callback URL")

    facebook_client_id: Optional[str] = Field(default=None, description="Facebook OAuth client ID")
    facebook_client_secret: Optional[str] = Field(default=None, description="Facebook OAuth client secret")
    facebook_callback_url: Optional[str] = Field(default=None, description="Facebook OAuth callback URL")

    # OpenID Configuration
    openid_issuer: Optional[str] = Field(default=None, description="OpenID issuer")
    openid_client_id: Optional[str] = Field(default=None, description="OpenID client ID")
    openid_client_secret: Optional[str] = Field(default=None, description="OpenID client secret")
    openid_callback_url: Optional[str] = Field(default=None, description="OpenID callback URL")
    openid_scope: str = Field(default="openid profile email", description="OpenID scope")

    # SAML Configuration
    saml_entity_id: Optional[str] = Field(default=None, description="SAML entity ID")
    saml_callback_url: Optional[str] = Field(default=None, description="SAML callback URL")
    saml_issuer: Optional[str] = Field(default=None, description="SAML issuer")
    saml_cert: Optional[str] = Field(default=None, description="SAML certificate")

    # Email Configuration
    email_enabled: bool = Field(default=False, description="Enable email")
    email_from: Optional[str] = Field(default=None, description="Email from address")
    email_from_name: Optional[str] = Field(default="LibreChat", description="Email from name")
    smtp_host: Optional[str] = Field(default=None, description="SMTP host")
    smtp_port: int = Field(default=587, description="SMTP port")
    smtp_username: Optional[str] = Field(default=None, description="SMTP username")
    smtp_password: Optional[str] = Field(default=None, description="SMTP password")
    smtp_use_tls: bool = Field(default=True, description="SMTP use TLS")

    # File Storage Configuration
    file_storage_type: str = Field(default="local", description="File storage type (local, s3, azure)")
    file_upload_max_size: int = Field(default=20971520, description="Max file upload size (20MB)")

    # S3 Configuration
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS access key ID")
    aws_secret_access_key: Optional[str] = Field(default=None, description="AWS secret access key")
    aws_region: str = Field(default="us-east-1", description="AWS region")
    s3_bucket: Optional[str] = Field(default=None, description="S3 bucket name")

    # Azure Blob Storage Configuration
    azure_storage_account: Optional[str] = Field(default=None, description="Azure storage account")
    azure_storage_key: Optional[str] = Field(default=None, description="Azure storage key")
    azure_container: Optional[str] = Field(default=None, description="Azure container name")

    # Meilisearch Configuration
    meili_host: Optional[str] = Field(default="http://localhost:7700", description="Meilisearch host")
    meili_key: Optional[str] = Field(default=None, description="Meilisearch API key")
    enable_meilisearch: bool = Field(default=True, description="Enable Meilisearch")

    # AI Configuration
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    google_api_key: Optional[str] = Field(default=None, description="Google API key")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    login_max_attempts: int = Field(default=5, description="Max login attempts")
    login_window_minutes: int = Field(default=15, description="Login window in minutes")

    # Registration
    allow_registration: bool = Field(default=True, description="Allow user registration")
    allow_email_verification: bool = Field(default=False, description="Require email verification")
    allow_social_login: bool = Field(default=True, description="Allow social login")

    # User Management
    allow_account_deletion: bool = Field(default=True, description="Allow account deletion")

    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_file: Optional[str] = Field(default=None, description="Log file path")

    # Compression
    enable_compression: bool = Field(default=True, description="Enable response compression")

    # Trust Proxy
    trust_proxy: bool = Field(default=False, description="Trust proxy headers")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("allowed_domains", mode="before")
    @classmethod
    def parse_allowed_domains(cls, v):
        """Parse allowed domains from string or list"""
        if v is None:
            return None
        if isinstance(v, str):
            return [domain.strip() for domain in v.split(",")]
        return v


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
