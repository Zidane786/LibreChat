"""Authentication utilities"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.config import get_settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token

    Args:
        data: Data to encode in token
        expires_delta: Optional token expiration delta

    Returns:
        Encoded JWT token
    """
    settings = get_settings()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=settings.jwt_expiration)

    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT refresh token

    Args:
        data: Data to encode in token
        expires_delta: Optional token expiration delta

    Returns:
        Encoded JWT refresh token
    """
    settings = get_settings()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=settings.jwt_refresh_expiration)

    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_refresh_secret,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Decode and verify JWT token

    Args:
        token: JWT token to decode
        token_type: Type of token ('access' or 'refresh')

    Returns:
        Decoded token payload or None if invalid
    """
    settings = get_settings()

    try:
        # Choose correct secret based on token type
        secret = (
            settings.jwt_secret
            if token_type == "access"
            else settings.jwt_refresh_secret
        )

        payload = jwt.decode(
            token,
            secret,
            algorithms=[settings.jwt_algorithm]
        )

        # Verify token type
        if payload.get("type") != token_type:
            return None

        return payload
    except JWTError:
        return None


def create_password_reset_token(email: str) -> str:
    """
    Create password reset token

    Args:
        email: User email address

    Returns:
        Encoded reset token
    """
    settings = get_settings()
    expires = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry

    to_encode = {
        "sub": email,
        "exp": expires,
        "type": "password_reset"
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify password reset token and return email

    Args:
        token: Reset token

    Returns:
        Email address if token is valid, None otherwise
    """
    try:
        payload = decode_token(token, token_type="password_reset")
        if payload and payload.get("type") == "password_reset":
            return payload.get("sub")
        return None
    except JWTError:
        return None
