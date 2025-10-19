"""
Authentication-related schemas for OAuth and token management.
"""

from pydantic import BaseModel, Field

from .user import UserResponse


# ============================================================================
# Authentication Schemas
# ============================================================================

class Token(BaseModel):
    """JWT token schema."""
    
    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenResponse(BaseModel):
    """Complete token response with user information."""
    
    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Token expiration time in seconds")
    user: UserResponse = Field(description="User information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "full_name": "John Doe"
                }
            }
        }


class RefreshTokenRequest(BaseModel):
    """Request to refresh access token."""
    
    refresh_token: str = Field(description="Refresh token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class GoogleOAuthRequest(BaseModel):
    """Google Sign-In authentication request."""
    
    id_token: str = Field(description="Google ID token from Sign-In")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjM..."
            }
        }


class GoogleTestLoginRequest(BaseModel):
    """Testing-only login request (bypasses Google verification)."""
    
    email: str = Field(description="User email")
    full_name: str = Field(default="Test User", description="Full name")
    profile_picture_url: str = Field(default=None, description="Profile picture URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "test@example.com",
                "full_name": "Test User",
                "profile_picture_url": "https://example.com/photo.jpg"
            }
        }

