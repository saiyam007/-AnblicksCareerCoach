"""
User management endpoints for profile operations.
"""

from fastapi import APIRouter, Depends, status

from ..models.userModel import User
from ..services.new_userServices import get_current_active_user
from ..services.registrationServices import RegistrationService, get_registration_service
from ..schemas import UserResponse, UserRegistrationResponse
from ..schemas.userState import UserJourneyStateResponse
from ..utils.apiHelper import get_logger
from ..schemas.common import success_response
from ..utils.errorHandler import NotFoundError
from ..services.new_stageServices import get_stage_service
from ..services.new_userStateServices import get_user_state_service


logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User Profile",
    description="Get the profile of the currently authenticated user"
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """
    Get current user's profile information including journey stage.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: User profile information with journey stage
    """
    logger.info(f"User profile retrieved: {current_user.email}")
    
    # Get user data
    user_data = current_user.to_dict()
    
    # Get current journey stage
    stage_service = get_stage_service()
    current_stage = stage_service.get_user_stage(current_user.email)
    
    # Add stage to user data
    user_data["journey_stage"] = current_stage or "AUTHENTICATED"
    
    return UserResponse.model_validate(user_data)


@router.get(
    "/me/details",
    response_model=UserRegistrationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get My User Details",
    description="Get user career details (type, education, career goals)"
)
async def get_my_user_details(
    current_user: User = Depends(get_current_active_user),
    registration_service: RegistrationService = Depends(get_registration_service)
) -> UserRegistrationResponse:
    """
    Get user career details for the current authenticated user.
    
    This endpoint retrieves the user's career details including
    their type (Student/Professional), current education/work information, 
    and future career goals.
    
    Args:
        current_user: Current authenticated user (from token)
        registration_service: Registration service
        
    Returns:
        UserRegistrationResponse: User's career details
        
    Raises:
        NotFoundError: If user details not found (user needs to complete registration)
        AuthenticationError: If user is not authenticated
    """
    user_details = await registration_service.get_registration(current_user)
    
    if not user_details:
        raise NotFoundError(
            message="User details not found. Please complete your profile first.",
            details={"u_id": current_user.id}
        )
    
    logger.info(f"User details retrieved for: {current_user.email}")
    
    return user_details


@router.get(
    "/me/state",
    response_model=UserJourneyStateResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Complete User Journey State",
    description="Get comprehensive user journey state with all data needed by frontend"
)
async def get_user_journey_state(
    current_user: User = Depends(get_current_active_user)
) -> UserJourneyStateResponse:
    """
    Get complete user journey state with all available data.
    
    This endpoint provides everything the frontend needs to:
    - Show the user where they are in their journey
    - Prepopulate forms with existing data
    - Display available next actions
    - Show progress indicators
    
    **Returns based on current stage:**
    - **AUTHENTICATED**: Basic user info only
    - **BASIC_REGISTERED**: User info + registration data
    - **PROFILE_COMPLETED**: User info + registration data
    - **CAREER_PATHS_GENERATED**: User info + registration + questions data
    - **ROADMAP_GENERATED**: User info + registration + questions + answers + roadmap
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Complete user journey state with all available data
        
    Raises:
        AuthenticationError: If user is not authenticated
    """
    logger.info(f"Getting complete journey state for user: {current_user.email}")
    
    # Get user state service
    state_service = get_user_state_service()
    
    # Get complete journey state
    journey_state = state_service.get_journey_state(current_user.email)
    
    # journey_state is already a dictionary
    state_data = journey_state
    
    logger.info(f"Retrieved complete journey state for user: {current_user.email}")
    
    # Return standardized response
    return success_response(
        data=state_data,
        message=f"User journey state retrieved successfully. Current stage: {state_data.get('journey_stage', 'UNKNOWN')}",
        code=200
    )


## Removed update and delete endpoints for minimal profile-only API
## Note: Journey stage is now included in /me endpoint response


