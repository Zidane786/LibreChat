"""Custom exception classes"""
from typing import Any, Optional


class LibreChatException(Exception):
    """Base exception for LibreChat"""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class AuthenticationError(LibreChatException):
    """Authentication failed"""
    def __init__(self, message: str = "Authentication failed", details: Optional[Any] = None):
        super().__init__(message, status_code=401, details=details)


class AuthorizationError(LibreChatException):
    """Authorization/permission denied"""
    def __init__(self, message: str = "Permission denied", details: Optional[Any] = None):
        super().__init__(message, status_code=403, details=details)


class NotFoundError(LibreChatException):
    """Resource not found"""
    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None):
        super().__init__(message, status_code=404, details=details)


class ValidationError(LibreChatException):
    """Validation error"""
    def __init__(self, message: str = "Validation failed", details: Optional[Any] = None):
        super().__init__(message, status_code=422, details=details)


class ConflictError(LibreChatException):
    """Resource conflict (e.g., duplicate)"""
    def __init__(self, message: str = "Resource conflict", details: Optional[Any] = None):
        super().__init__(message, status_code=409, details=details)


class RateLimitError(LibreChatException):
    """Rate limit exceeded"""
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Any] = None):
        super().__init__(message, status_code=429, details=details)


class DatabaseError(LibreChatException):
    """Database operation failed"""
    def __init__(self, message: str = "Database error", details: Optional[Any] = None):
        super().__init__(message, status_code=500, details=details)
