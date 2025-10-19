"""
AI User Routes - User management for AI Users table.

Simple user profile CRUD operations for the AI Users table.
This is separate from Backend's main user management system.

These endpoints work with a separate 'Users' DynamoDB table that uses:
- Partition Key: email
- Sort Key: recordId
"""

from fastapi import APIRouter, status, Depends, HTTPException

# Import models
from ..models.userModel import User

# Import schemas
from ..schemas.aiUser import (
    CompleteProfileRequest,
    StandardProfileResponse
)
from ..schemas.common import success_response

# Import service layer
from ..services.aiUserServices import get_ai_user_service
from ..services.new_userServices import get_current_active_user
from ..utils.errorHandler import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter()

# Get service instance
ai_user_service = get_ai_user_service()


# ============================================================================
# Endpoints
# ============================================================================

@router.post(
    "/users/complete-profile",
    response_model=StandardProfileResponse,
    summary="Complete User Profile (After Sign-In)",
    description="Complete user profile with career details and auto-generate AI summary",
    response_description="Standard response with user data including AI-generated summary",
    status_code=status.HTTP_200_OK,
    tags=["AI User Management"]
)
async def complete_user_profile(
    user_data: CompleteProfileRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Complete user profile after Google sign-in.
    
    **Authentication Required:** User must be signed in (JWT token in header).
    
    This endpoint:
    1. Takes registration form data
    2. Automatically generates AI profile summary
    3. Updates the authenticated user's profile
    4. Saves everything to Users table
    
    **Flow:**
    - User signs in with Google → Gets JWT token
    - User fills registration form
    - Frontend sends form data + JWT token
    - Backend updates user profile + generates AI summary
    
    Args:
        user_data: Registration form data (career details)
        current_user: Authenticated user from JWT token
        
    Returns:
        Success message with complete profile including AI summary
        
    Raises:
        HTTPException: If update fails or AI generation fails
    """
    logger.info(f"Complete profile request for authenticated user: {current_user.email}")
    
    # Convert Pydantic model to dict
    user_dict = user_data.model_dump()
    
    # Override email with authenticated user's email (security)
    user_dict["email"] = current_user.email
    
    # Add user info that might not be in the form
    if not user_dict.get("firstName"):
        user_dict["firstName"] = current_user.first_name or ""
    if not user_dict.get("lastName"):
        user_dict["lastName"] = current_user.last_name or ""
    
    # Call service layer (generates AI summary + saves)
    result = ai_user_service.register_user(user_dict)
    
    # Return standardized response
    return success_response(
        data=result["user"],
        message="Profile completed successfully with AI-generated summary",
        code=200
    )








