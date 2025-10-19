"""
User-related schemas for API requests and responses.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator

from ..models.enums import UserRole, UserStatus, AuthProvider, JourneyStage


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
    journey_stage: Optional[str] = Field(default=None, description="Current journey stage for frontend redirection")
    
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
                "last_login_at": "2024-01-15T10:30:00",
                "journey_stage": "PROFILE_COMPLETED"
            }
        }

