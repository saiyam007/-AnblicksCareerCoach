"""
Registration-related schemas for user career registration.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


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

