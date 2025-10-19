"""
AI Career Advisor Schemas.

Request and response schemas for AI-powered career advisor endpoints:
- Question generation
- Roadmap generation
- Profile summary generation
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr


# ============================================================================
# Request Schemas
# ============================================================================



class UserAnswer(BaseModel):
    """User answer to a generated question."""
    id: str = Field(..., description="Question ID")
    text: str = Field(..., description="Question text")
    answer: str = Field(..., alias="type", description="User's answer: Yes, No, Agree, Disagree, Not Sure")

    class Config:
        populate_by_name = True  # Allow both "answer" and "type"
        json_schema_extra = {
            "example": {
                "id": "q1",
                "text": "Do you have experience with machine learning frameworks?",
                "type": "yes"
            }
        }






# ============================================================================
# Response Schemas
# ============================================================================

class Question(BaseModel):
    """Generated question schema."""
    id: str = Field(..., description="Question ID")
    text: str = Field(..., description="Question text")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "q1",
                "text": "Do you have experience with machine learning frameworks?"
            }
        }




class CareerPath(BaseModel):
    """Career path recommendation schema."""
    title: str = Field(..., description="Career path title")
    description: str = Field(..., description="Career path description")
    timeToAchieve: str = Field(..., description="Estimated time to achieve")
    averageSalary: str = Field(..., description="Average salary range")
    keySkillsRequired: List[str] = Field(..., description="Required skills")
    learningRoadmap: List[str] = Field(..., description="Learning steps")
    aiRecommendation: dict = Field(..., description="AI recommendation with reasoning")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Machine Learning Engineer",
                "description": "Design and deploy ML models...",
                "timeToAchieve": "6-12 months",
                "averageSalary": "₹18-20 LPA (India), $90,000-150,000 (USA)",
                "keySkillsRequired": ["Python", "TensorFlow", "MLOps"],
                "learningRoadmap": ["Master ML algorithms", "Learn MLOps tools"],
                "aiRecommendation": {"reason": "Your experience makes you a great fit..."}
            }
        }






# ============================================================================
# Standard Response Wrappers (for User Journey endpoints)
# ============================================================================

class StandardQuestionsResponse(BaseModel):
    """Standard response wrapper for questions generation."""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Dict[str, Any] = Field(..., description="Generated questions data with roadmapId")
    error: None = Field(None, description="Error details (null on success)")
    code: int = Field(200, description="HTTP status code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Retrieved 5 career questions successfully",
                "data": {
                    "questions": {
                        "questions": [
                            {"id": "q1", "text": "Do you have Python experience?"},
                            {"id": "q2", "text": "Are you familiar with ML?"}
                        ]
                    },
                    "roadmapId": "550e8400-e29b-41d4-a716-446655440000"
                },
                "error": None,
                "code": 200
            }
        }


class StandardRoadmapResponse(BaseModel):
    """Standard response wrapper for roadmap generation."""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Dict[str, Any] = Field(..., description="Generated roadmap data")
    error: None = Field(None, description="Error details (null on success)")
    code: int = Field(200, description="HTTP status code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Career roadmap generated successfully with 5 paths",
                "data": {
                    "careerPaths": [
                        {
                            "title": "Machine Learning Engineer",
                            "description": "Design and deploy ML models",
                            "timeToAchieve": "6-12 months",
                            "averageSalary": "₹18-20 LPA",
                            "keySkillsRequired": ["Python", "TensorFlow"],
                            "learningRoadmap": ["Step 1", "Step 2"],
                            "aiRecommendation": {"reason": "Perfect fit..."}
                        }
                    ]
                },
                "error": None,
                "code": 200
            }
        }

