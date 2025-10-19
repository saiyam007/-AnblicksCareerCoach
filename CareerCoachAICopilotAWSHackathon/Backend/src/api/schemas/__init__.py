"""
Schemas package - exports all schema models for easy importing.

Usage:
    from src.api.schemas import UserResponse, TokenResponse, etc.
"""

# Common schemas
from .common import (
    ResponseModel,
    HealthCheck,
    ErrorResponse,
)

# User schemas
from .user import (
    UserBase,
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
)

# Authentication schemas
from .auth import (
    Token,
    TokenResponse,
    RefreshTokenRequest,
    GoogleOAuthRequest,
    GoogleTestLoginRequest,
)

# Registration schemas
from .registration import (
    CurrentInfo,
    FutureInfo,
    PrimaryDetails,
    UserRegistrationRequest,
    MetaInfo,
    UserRegistrationResponse,
)

__all__ = [
    # Common
    "ResponseModel",
    "HealthCheck",
    "ErrorResponse",
    
    # User
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    
    # Auth
    "Token",
    "TokenResponse",
    "RefreshTokenRequest",
    "GoogleOAuthRequest",
    "GoogleTestLoginRequest",
    
    # Registration
    "CurrentInfo",
    "FutureInfo",
    "PrimaryDetails",
    "UserRegistrationRequest",
    "MetaInfo",
    "UserRegistrationResponse",
]

