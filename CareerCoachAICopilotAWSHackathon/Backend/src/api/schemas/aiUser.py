"""
AI User Management Schemas.

Request and response schemas for AI Users table operations:
- User registration
- User retrieval
- Profile updates
"""

from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


# ============================================================================
# Request Schemas
# ============================================================================

class CompleteProfileRequest(BaseModel):
    """Request schema for completing profile (authenticated endpoint - email from JWT)."""
    firstName: Optional[str] = Field(None, description="First name (optional, from Google)")
    lastName: Optional[str] = Field(None, description="Last name (optional, from Google)")
    country: str = Field(..., description="Country")
    state: str = Field(..., description="State/Province")
    userType: str = Field(..., description="Student or Professional")
    careerGoal: Optional[str] = Field(None, description="Career goal")
    lookingFor: Optional[str] = Field(None, description="What user is looking for")
    languagePreference: Optional[str] = Field(None, description="Language preference")
    currentEducationLevel: Optional[str] = Field(None, description="Education level")
    fieldOfStudy: Optional[str] = Field(None, description="Field of study")
    academicInterests: Optional[str] = Field(None, description="Academic interests")
    preferredStudyDestination: Optional[str] = Field(None, description="Study destination")
    currentJobTitle: Optional[str] = Field(None, description="Job title (for professionals)")
    industry: Optional[str] = Field(None, description="Industry")
    
    class Config:
        json_schema_extra = {
            "example": {
                "country": "India",
                "state": "Gujarat",
                "userType": "Student",
                "careerGoal": "AI Engineer",
                "fieldOfStudy": "Computer Science",
                "currentEducationLevel": "Master degree",
                "academicInterests": "Machine Learning",
                "lookingFor": "Skill Development",
                "languagePreference": "English"
            }
        }






# ============================================================================
# Response Schemas
# ============================================================================

class AIUserResponse(BaseModel):
    """Response schema for AI user data."""
    email: str = Field(..., description="User email")
    recordId: str = Field(..., description="Record ID (PROFILE#LATEST)")
    firstName: str = Field(..., description="First name")
    lastName: str = Field(..., description="Last name")
    country: str = Field(..., description="Country")
    state: str = Field(..., description="State/Province")
    userType: str = Field(..., description="User type")
    careerGoal: Optional[str] = Field(None, description="Career goal")
    fieldOfStudy: Optional[str] = Field(None, description="Field of study")
    profile_summary: Optional[str] = Field(None, description="Profile summary")
    updatedAt: str = Field(..., description="Last update timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "recordId": "PROFILE#LATEST",
                "firstName": "John",
                "lastName": "Doe",
                "country": "USA",
                "state": "California",
                "userType": "Student",
                "careerGoal": "Data Scientist",
                "fieldOfStudy": "Computer Science",
                "updatedAt": "2025-10-13T01:00:00.000000"
            }
        }


class AIUserCreateResponse(BaseModel):
    """Response schema for user creation."""
    message: str = Field(..., description="Success message")
    user: dict = Field(..., description="Created user data with AI-generated summary")
    ai_summary_generated: bool = Field(..., description="Whether AI summary was successfully generated")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "User registered successfully",
                "user": {
                    "email": "john.doe@example.com",
                    "firstName": "John",
                    "lastName": "Doe",
                    "profile_summary": "AI-generated summary..."
                },
                "ai_summary_generated": True
            }
        }






# ============================================================================
# Standard Response Wrappers
# ============================================================================

class StandardProfileResponse(BaseModel):
    """Standard response wrapper for profile completion."""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: dict = Field(..., description="User profile data with AI summary")
    error: None = Field(None, description="Error details (null on success)")
    code: int = Field(200, description="HTTP status code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Profile completed successfully with AI-generated summary",
                "data": {
                    "email": "user@example.com",
                    "firstName": "John",
                    "lastName": "Doe",
                    "careerGoal": "AI Engineer",
                    "profile_summary": "AI-generated summary here..."
                },
                "error": None,
                "code": 200
            }
        }

