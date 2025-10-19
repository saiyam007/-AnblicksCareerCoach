"""
Registration endpoints for user career registration.
"""

from fastapi import APIRouter, Depends, status

from ..models.userModel import User
from ..services.new_userServices import get_current_active_user
from ..services.new_registrationServices import NewRegistrationService, get_new_registration_service
from ..schemas import (
    UserRegistrationRequest,
    UserRegistrationResponse,
)
from ..utils.apiHelper import get_logger


logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=UserRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create or Update User Details",
    description="Create or update user career details (acts as upsert - requires authentication)"
)
async def create_registration(
    registration_data: UserRegistrationRequest,
    current_user: User = Depends(get_current_active_user),
    registration_service: NewRegistrationService = Depends(get_new_registration_service)
) -> UserRegistrationResponse:
    """
    Create or update user career details (UPSERT operation).
    
    This endpoint allows authenticated users to save their career information.
    - If user details don't exist → Creates new entry
    - If user details exist → Updates existing entry (no duplicates!)
    
    **Required fields:**
    - type: "Student" or "Professional"
    - primary_details.current_info (education_level, field, etc.)
    - future_info (career_goal, looking_for, etc.)
    
    **Auto-populated from token:**
    - id: Auto-generated UUID (or reuses existing if updating)
    - u_id: User ID from authentication token
    - email: User email from authentication token
    
    Args:
        registration_data: Registration data (type, primary_details, future_info)
        current_user: Current authenticated user (from token)
        registration_service: Registration service
        
    Returns:
        UserRegistrationResponse: Created/updated registration with all details
        
    Raises:
        ValidationError: If validation fails (invalid type or missing fields)
        AuthenticationError: If user is not authenticated
    """
    registration = await registration_service.create_registration(
        user=current_user,
        registration_data=registration_data
    )
    
    logger.info(f"Registration created for user: {current_user.email}")
    
    return registration



