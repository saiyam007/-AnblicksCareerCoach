"""
Centralized Pydantic schemas for API requests and responses.
"""

from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, EmailStr, Field, validator

from .models.enums import UserRole, UserStatus, AuthProvider


# ============================================================================
# Common Response Models
# ============================================================================

DataT = TypeVar("DataT")


class ResponseModel(BaseModel):
    """
    Standard API response model.
    
    Provides consistent response structure across all endpoints.
    """
    
    status: str = Field(default="success", description="Response status")
    message: str = Field(default="Success", description="Human-readable message")
    data: Optional[Any] = Field(default=None, description="Response data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Operation completed successfully",
                "data": {"id": 1, "name": "Example"}
            }
        }


## Removed pagination model for minimal API


class HealthCheck(BaseModel):
    """Health check response."""
    
    status: str = Field(default="healthy", description="Service health status")
    version: str = Field(description="API version")
    environment: str = Field(description="Environment name")
    database: str = Field(default="connected", description="Database connection status")


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: EmailStr = Field(description="User email address")
    full_name: Optional[str] = Field(default=None, max_length=100, description="Full name")
    first_name: Optional[str] = Field(default=None, max_length=100, description="First name")
    last_name: Optional[str] = Field(default=None, max_length=100, description="Last name")
    phone_number: Optional[str] = Field(default=None, max_length=20, description="Phone number")
    
    class Config:
        from_attributes = True


class UserCreate(UserBase):
    """Schema for creating a new user."""
    
    password: str = Field(min_length=8, max_length=100, description="User password")
    
    @validator("password")
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123",
                "full_name": "John Doe",
                "phone_number": "+1234567890"
            }
        }


class UserLogin(BaseModel):
    """Schema for user login."""
    
    email: EmailStr = Field(description="User email address")
    password: str = Field(description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    
    full_name: Optional[str] = Field(default=None, max_length=100)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    phone_number: Optional[str] = Field(default=None, max_length=20)
    profile_picture_url: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe Updated",
                "phone_number": "+1234567890"
            }
        }


class UserResponse(UserBase):
    """Schema for user response."""
    
    id: str = Field(description="User ID (UUID)")
    auth_provider: AuthProvider = Field(description="Authentication provider")
    profile_picture_url: Optional[str] = None
    is_active: bool = Field(description="Account active status")
    is_verified: bool = Field(description="Email verification status")
    status: UserStatus = Field(description="Account status")
    role: UserRole = Field(description="User role")
    created_at: datetime = Field(description="Account creation timestamp")
    last_login_at: Optional[datetime] = Field(default=None, description="Last login timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "full_name": "John Doe",
                "auth_provider": "google",
                "is_active": True,
                "is_verified": True,
                "status": "active",
                "role": "user",
                "created_at": "2024-01-01T00:00:00",
                "last_login_at": "2024-01-15T10:30:00"
            }
        }


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


## Removed password-related schema for minimal Google SSO only


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    error: str
    message: str
    details: Optional[Any] = None
    path: Optional[str] = None
    status_code: int


# ============================================================================
# Registration Schemas
# ============================================================================

class CurrentInfo(BaseModel):
    """Current information schema for user registration."""
    
    education_level: str = Field(description="Education level: Student or Professional")
    field: str = Field(description="Field of study or work")
    academic_interest: Optional[str] = Field(default=None, description="Academic interest")
    preferred_study_destination: Optional[str] = Field(default=None, description="Preferred study destination")
    
    class Config:
        json_schema_extra = {
            "example": {
                "education_level": "Student",
                "field": "Science",
                "academic_interest": "Computer engineering",
                "preferred_study_destination": "UK"
            }
        }


class FutureInfo(BaseModel):
    """Future information schema for user registration."""
    
    career_goal: str = Field(description="Career goal")
    looking_for: str = Field(description="What user is looking for")
    language_preference: Optional[str] = Field(default=None, description="Language preference")
    
    class Config:
        json_schema_extra = {
            "example": {
                "career_goal": "data science",
                "looking_for": "Job search",
                "language_preference": "English"
            }
        }


class PrimaryDetails(BaseModel):
    """Primary details schema for user registration."""
    
    current_info: CurrentInfo = Field(description="Current information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_info": {
                    "education_level": "Student",
                    "field": "Science",
                    "academic_interest": "Computer engineering",
                    "preferred_study_destination": "UK"
                }
            }
        }


class UserRegistrationRequest(BaseModel):
    """User registration request schema."""
    
    type: str = Field(description="User type: Student or Professional", pattern="^(Student|Professional)$")
    primary_details: PrimaryDetails = Field(description="Primary details")
    future_info: FutureInfo = Field(description="Future information")
    
    @validator("type")
    def validate_type(cls, v):
        """Validate user type."""
        if v not in ["Student", "Professional"]:
            raise ValueError("Type must be either 'Student' or 'Professional'")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "Student",
                "primary_details": {
                    "current_info": {
                        "education_level": "Student",
                        "field": "Science",
                        "academic_interest": "Computer engineering",
                        "preferred_study_destination": "UK"
                    }
                },
                "future_info": {
                    "career_goal": "data science",
                    "looking_for": "Job search",
                    "language_preference": "English"
                }
            }
        }


class MetaInfo(BaseModel):
    """Meta information schema."""
    
    stage: str = Field(default="REGISTRATION", description="Registration stage")


class UserRegistrationResponse(BaseModel):
    """User registration response schema."""
    
    id: str = Field(description="Registration ID (UUID)")
    u_id: str = Field(description="User ID (logged in user)")
    email: str = Field(description="User email")
    type: str = Field(description="User type")
    meta: MetaInfo = Field(description="Meta information")
    primary_details: PrimaryDetails = Field(description="Primary details")
    future_info: FutureInfo = Field(description="Future information")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Update timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "u_id": "user-uuid-123",
                "email": "tarunpatel@gmail.com",
                "type": "Student",
                "meta": {
                    "stage": "REGISTRATION"
                },
                "primary_details": {
                    "current_info": {
                        "education_level": "Student",
                        "field": "Science",
                        "academic_interest": "Computer engineering",
                        "preferred_study_destination": "UK"
                    }
                },
                "future_info": {
                    "career_goal": "data science",
                    "looking_for": "Job search",
                    "language_preference": "English"
                },
                "created_at": "2025-10-10T12:00:00",
                "updated_at": "2025-10-10T12:00:00"
            }
        }


