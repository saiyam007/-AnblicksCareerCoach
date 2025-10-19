"""
User Journey State Schemas.

Pydantic models for comprehensive user journey state management:
- Complete state response with all data needed by frontend
- Stage-specific data structures
- Next actions and progress tracking
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from .auth import UserResponse
from .registration import UserRegistrationResponse


# ============================================================================
# Stage-Specific Data Models
# ============================================================================

class StageInfo(BaseModel):
    """Information about a journey stage."""
    stage: str = Field(..., description="Current journey stage")
    order: int = Field(..., description="Stage order number")
    description: str = Field(..., description="Human-readable stage description")
    is_valid: bool = Field(..., description="Whether stage is valid")


class ProgressInfo(BaseModel):
    """User progress information."""
    current_step: int = Field(..., description="Current step number")
    total_steps: int = Field(..., description="Total steps in journey")
    progress_percentage: float = Field(..., description="Progress as percentage")
    completed_steps: List[str] = Field(..., description="List of completed stages")


class NextAction(BaseModel):
    """Next available action for user."""
    action: str = Field(..., description="Action identifier")
    title: str = Field(..., description="Human-readable action title")
    description: str = Field(..., description="Action description")
    endpoint: str = Field(..., description="API endpoint to call")
    method: str = Field(..., description="HTTP method")
    requires_data: bool = Field(..., description="Whether action requires request data")


# ============================================================================
# Stage-Specific Data Containers
# ============================================================================

class CurrentData(BaseModel):
    """Current data available to user based on journey stage."""
    registration: Optional[UserRegistrationResponse] = Field(None, description="Registration data (if available)")
    questions: Optional[Dict[str, Any]] = Field(None, description="Generated questions (if available)")
    answers: Optional[List[Dict[str, Any]]] = Field(None, description="User answers (if available)")
    roadmap: Optional[Dict[str, Any]] = Field(None, description="Generated roadmap (if available)")
    roadmap_id: Optional[str] = Field(None, description="Current roadmap ID")


# ============================================================================
# Main State Response Model
# ============================================================================

class UserJourneyStateResponse(BaseModel):
    """Complete user journey state response."""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Dict[str, Any] = Field(..., description="Complete user journey state")
    error: None = Field(None, description="Error details (null on success)")
    code: int = Field(200, description="HTTP status code")


# ============================================================================
# Internal State Data Model (for service layer)
# ============================================================================

class UserJourneyState(BaseModel):
    """Internal model for user journey state."""
    user: UserResponse = Field(..., description="User profile information")
    journey_stage: str = Field(..., description="Current journey stage")
    stage_info: StageInfo = Field(..., description="Stage information")
    progress: ProgressInfo = Field(..., description="Progress information")
    current_data: CurrentData = Field(..., description="Current available data")
    next_actions: List[NextAction] = Field(..., description="Available next actions")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last state update time")
