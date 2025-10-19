"""
Assessment API Schemas

Defines Pydantic models for assessment question generation and answer evaluation.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """User profile for generating assessment questions."""
    name: Optional[str] = Field(..., description="User's name")
    career_goal: str = Field(..., description="User's career goal")
    skill: str = Field(..., description="Skill to be assessed")
    experience: Optional[str] = Field(None, description="User's experience level")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Riya Shah",
                "career_goal": "To build a career in Human Resource Management",
                "skill": "Employee Engagement",
                "experience": "2 years"
            }
        }


class QuestionOption(BaseModel):
    """Multiple choice question option."""
    A: str
    B: str
    C: str
    D: str


class AssessmentQuestion(BaseModel):
    """Generated assessment question."""
    id: int = Field(..., description="Question ID")
    skill: str = Field(..., description="Skill being assessed")
    question: str = Field(..., description="Question text")
    options: Optional[Dict[str, str]] = Field(None, description="Multiple choice options (A, B, C, D)")
    difficulty: str = Field(..., description="Question difficulty: Medium or Hard")
    correct_answer: Optional[str] = Field(None, description="Correct answer (for MCQ)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "skill": "Employee Engagement",
                "question": "Which of the following is a key driver of employee engagement?",
                "options": {
                    "A": "High salaries",
                    "B": "Opportunities for growth",
                    "C": "Flexible working hours",
                    "D": "Free snacks in the office"
                },
                "difficulty": "Medium",
                "correct_answer": "B"
            }
        }


class ResponseItem(BaseModel):
    """User's response to an assessment question."""
    id: int = Field(..., description="Question ID")
    skill: str = Field(..., description="Skill being assessed")
    question: str = Field(..., description="Question text")
    difficulty: str = Field(..., description="Question difficulty")
    user_answer: str = Field(..., description="User's answer")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "skill": "Employee Engagement",
                "question": "Which of the following is a key driver of employee engagement?",
                "difficulty": "Medium",
                "user_answer": "High salaries"
            }
        }


class EvaluationRequest(BaseModel):
    """Request to evaluate user's assessment responses."""
    responses: List[ResponseItem] = Field(..., description="List of user responses")
    assessment_id: Optional[str] = Field(None, description="Assessment ID for database tracking")
    
    class Config:
        json_schema_extra = {
            "example": {
                "responses": [
                    {
                        "id": 1,
                        "skill": "Employee Engagement",
                        "question": "Which of the following is a key driver of employee engagement?",
                        "difficulty": "Medium",
                        "user_answer": "High salaries"
                    }
                ]
            }
        }


class EvaluationResult(BaseModel):
    """Evaluation result with scores and summary."""
    Skill: str = Field(..., description="Skill assessed")
    Total_Questions: int = Field(..., description="Total number of questions")
    Correct_Answers: int = Field(..., description="Number of correct answers")
    Intermidiate_score: str = Field(..., description="Percentage correct for medium difficulty questions")
    Advanced_score: str = Field(..., description="Percentage correct for hard difficulty questions")
    theory_question_score: str = Field(..., description="Percentage correct for theory questions")
    Overall: str = Field(..., description="Overall percentage score")
    Summary: List[str] = Field(..., description="List of feedback points")
    
    class Config:
        json_schema_extra = {
            "example": {
                "Skill": "Employee Engagement",
                "Total_Questions": 10,
                "Correct_Answers": 7,
                "Intermidiate_score": "75%",
                "Advanced_score": "60%",
                "theory_question_score": "80%",
                "Overall": "72%",
                "Summary": [
                    "Good understanding of engagement strategies and employee motivation.",
                    "Needs improvement in advanced techniques and data-driven approaches."
                ]
            }
        }


class AssessmentQuestionResponse(BaseModel):
    """Response for assessment question generation."""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: List[AssessmentQuestion] = Field(..., description="Generated questions")
    error: Optional[str] = Field(None, description="Error details (null on success)")
    code: int = Field(200, description="HTTP status code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Assessment questions generated successfully",
                "data": [
                    {
                        "id": 1,
                        "skill": "Employee Engagement",
                        "question": "Which of the following is a key driver of employee engagement?",
                        "options": {
                            "A": "High salaries",
                            "B": "Opportunities for growth",
                            "C": "Flexible working hours",
                            "D": "Free snacks in the office"
                        },
                        "difficulty": "Medium",
                        "correct_answer": "B"
                    }
                ],
                "error": None,
                "code": 200
            }
        }


class EvaluationResponse(BaseModel):
    """Response for assessment evaluation."""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: EvaluationResult = Field(..., description="Evaluation results")
    error: Optional[str] = Field(None, description="Error details (null on success)")
    code: int = Field(200, description="HTTP status code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Assessment evaluated successfully",
                "data": {
                    "Skill": "Employee Engagement",
                    "Total_Questions": 10,
                    "Correct_Answers": 7,
                    "Intermidiate_score": "75%",
                    "Advanced_score": "60%",
                    "theory_question_score": "80%",
                    "Overall": "72%",
                    "Summary": [
                        "Good understanding of engagement strategies and employee motivation.",
                        "Needs improvement in advanced techniques and data-driven approaches."
                    ]
                },
                "error": None,
                "code": 200
            }
        }

