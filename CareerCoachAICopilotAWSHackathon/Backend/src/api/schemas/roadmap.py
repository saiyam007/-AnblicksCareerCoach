"""
Roadmap Schemas for UserCareerRoadmaps table.

Pydantic models for roadmap data structures and API responses:
- Roadmap status tracking
- Question and answer storage
- Career path recommendations
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class RoadmapStatus(str, Enum):
    """Roadmap status enumeration."""
    QUESTIONS_GENERATED = "QUESTIONS_GENERATED"
    ROADMAP_COMPLETED = "ROADMAP_COMPLETED"


# ============================================================================
# Core Data Models
# ============================================================================

class RoadmapQuestion(BaseModel):
    """Question model for roadmap storage."""
    id: str = Field(..., description="Question ID")
    text: str = Field(..., description="Question text")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "q1",
                "text": "Do you have experience with machine learning frameworks?"
            }
        }


class RoadmapAnswer(BaseModel):
    """User answer model for roadmap storage."""
    id: str = Field(..., description="Question ID")
    text: str = Field(..., description="Question text")
    answer: str = Field(..., description="User's answer")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "q1",
                "text": "Do you have experience with machine learning frameworks?",
                "answer": "Yes"
            }
        }


class CareerPathRecommendation(BaseModel):
    """Career path recommendation model."""
    title: str = Field(..., description="Career path title")
    description: str = Field(..., description="Career path description")
    timeToAchieve: str = Field(..., description="Estimated time to achieve")
    averageSalary: str = Field(..., description="Average salary range")
    keySkillsRequired: List[str] = Field(..., description="Required skills")
    learningRoadmap: List[str] = Field(..., description="Learning steps")
    aiRecommendation: Dict[str, Any] = Field(..., description="AI recommendation with reasoning")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Machine Learning Engineer",
                "description": "Design and deploy ML models for production systems",
                "timeToAchieve": "6-12 months",
                "averageSalary": "₹18-20 LPA (India), $90,000-150,000 (USA)",
                "keySkillsRequired": ["Python", "TensorFlow", "MLOps", "Statistics"],
                "learningRoadmap": [
                    "Master ML algorithms and statistics",
                    "Learn MLOps tools and deployment",
                    "Build portfolio projects",
                    "Get industry certifications"
                ],
                "aiRecommendation": {
                    "reason": "Your computer science background and interest in data science make you an excellent fit for ML engineering roles",
                    "confidence": "85%"
                }
            }
        }


class RoadmapData(BaseModel):
    """Complete roadmap data model."""
    careerPaths: List[CareerPathRecommendation] = Field(..., description="List of career path recommendations")

    class Config:
        json_schema_extra = {
            "example": {
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
            }
        }


# ============================================================================
# Database Models
# ============================================================================

class RoadmapRecord(BaseModel):
    """Complete roadmap record from database."""
    email: str = Field(..., description="User email")
    roadmapId: str = Field(..., description="Unique roadmap identifier")
    status: RoadmapStatus = Field(..., description="Current roadmap status")
    questions: Optional[Dict[str, Any]] = Field(None, description="Generated questions")
    answers: Optional[List[Dict[str, Any]]] = Field(None, description="User answers")
    roadmap: Optional[Dict[str, Any]] = Field(None, description="Generated roadmap")
    profile: Optional[Dict[str, Any]] = Field(None, description="User profile snapshot")
    createdAt: str = Field(..., description="Creation timestamp")
    updatedAt: str = Field(..., description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "roadmapId": "550e8400-e29b-41d4-a716-446655440000",
                "status": "ROADMAP_COMPLETED",
                "questions": {
                    "questions": [
                        {"id": "q1", "text": "Do you have ML experience?"}
                    ]
                },
                "answers": [
                    {"id": "q1", "text": "Do you have ML experience?", "answer": "Yes"}
                ],
                "roadmap": {
                    "careerPaths": [
                        {
                            "title": "ML Engineer",
                            "description": "Design ML systems",
                            "timeToAchieve": "6-12 months",
                            "averageSalary": "₹18-20 LPA",
                            "keySkillsRequired": ["Python", "TensorFlow"],
                            "learningRoadmap": ["Step 1", "Step 2"],
                            "aiRecommendation": {"reason": "Great fit"}
                        }
                    ]
                },
                "profile": {
                    "userType": "Student",
                    "careerGoal": "Data Scientist"
                },
                "createdAt": "2024-01-15T10:30:00Z",
                "updatedAt": "2024-01-15T11:45:00Z"
            }
        }


# ============================================================================
# API Request Models
# ============================================================================

class QuestionsGenerationRequest(BaseModel):
    """Request model for question generation (no body needed)."""
    pass

    class Config:
        json_schema_extra = {
            "description": "Generate career questions for the authenticated user. No request body required."
        }


class RoadmapGenerationRequest(BaseModel):
    """Request model for roadmap generation."""
    answers: List[RoadmapAnswer] = Field(..., description="User answers to generated questions")

    class Config:
        json_schema_extra = {
            "example": {
                "answers": [
                    {
                        "id": "q1",
                        "text": "Do you have experience with machine learning frameworks?",
                        "answer": "Yes"
                    },
                    {
                        "id": "q2",
                        "text": "Are you interested in specializing in robotics applications of AI?",
                        "answer": "Not Sure"
                    }
                ]
            }
        }


# ============================================================================
# API Response Models
# ============================================================================

class QuestionsGenerationResponse(BaseModel):
    """Response model for question generation."""
    questions: Dict[str, Any] = Field(..., description="Generated questions data")
    roadmapId: str = Field(..., description="Unique roadmap identifier for tracking")

    class Config:
        json_schema_extra = {
            "example": {
                "questions": {
                    "questions": [
                        {"id": "q1", "text": "Do you have ML experience?"},
                        {"id": "q2", "text": "Are you interested in robotics?"}
                    ]
                },
                "roadmapId": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class RoadmapGenerationResponse(BaseModel):
    """Response model for roadmap generation."""
    roadmap: Dict[str, Any] = Field(..., description="Generated career roadmap")
    roadmapId: str = Field(..., description="Roadmap identifier")

    class Config:
        json_schema_extra = {
            "example": {
                "roadmap": {
                    "careerPaths": [
                        {
                            "title": "Machine Learning Engineer",
                            "description": "Design and deploy ML models",
                            "timeToAchieve": "6-12 months",
                            "averageSalary": "₹18-20 LPA",
                            "keySkillsRequired": ["Python", "TensorFlow"],
                            "learningRoadmap": ["Step 1", "Step 2"],
                            "aiRecommendation": {"reason": "Perfect fit"}
                        }
                    ]
                },
                "roadmapId": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class RoadmapListResponse(BaseModel):
    """Response model for listing user roadmaps."""
    roadmaps: List[RoadmapRecord] = Field(..., description="List of user roadmaps")
    total_count: int = Field(..., description="Total number of roadmaps")

    class Config:
        json_schema_extra = {
            "example": {
                "roadmaps": [
                    {
                        "email": "user@example.com",
                        "roadmapId": "550e8400-e29b-41d4-a716-446655440000",
                        "status": "ROADMAP_COMPLETED",
                        "createdAt": "2024-01-15T10:30:00Z",
                        "updatedAt": "2024-01-15T11:45:00Z"
                    }
                ],
                "total_count": 1
            }
        }


# ============================================================================
# Utility Models
# ============================================================================

class RoadmapMetadata(BaseModel):
    """Roadmap metadata for summary views."""
    roadmapId: str = Field(..., description="Roadmap identifier")
    status: RoadmapStatus = Field(..., description="Current status")
    createdAt: str = Field(..., description="Creation timestamp")
    updatedAt: str = Field(..., description="Last update timestamp")
    questionCount: Optional[int] = Field(None, description="Number of questions generated")
    careerPathCount: Optional[int] = Field(None, description="Number of career paths recommended")

    class Config:
        json_schema_extra = {
            "example": {
                "roadmapId": "550e8400-e29b-41d4-a716-446655440000",
                "status": "ROADMAP_COMPLETED",
                "createdAt": "2024-01-15T10:30:00Z",
                "updatedAt": "2024-01-15T11:45:00Z",
                "questionCount": 5,
                "careerPathCount": 3
            }
        }


class RoadmapDeletionResult(BaseModel):
    """Result of roadmap deletion operation."""
    deleted_count: int = Field(..., description="Number of roadmaps deleted")
    message: str = Field(..., description="Deletion result message")

    class Config:
        json_schema_extra = {
            "example": {
                "deleted_count": 2,
                "message": "Successfully deleted 2 roadmaps for user profile update"
            }
        }
