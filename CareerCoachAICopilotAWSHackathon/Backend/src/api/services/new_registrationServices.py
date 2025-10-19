"""
New Registration Service using the normalized schema.
"""

from datetime import datetime
from typing import Optional
from fastapi import Depends

from ..models.userModel import User
from ..utils.database import get_db
from ..schemas import (
    UserRegistrationRequest,
    UserRegistrationResponse,
    MetaInfo,
    PrimaryDetails,
    CurrentInfo,
    FutureInfo,
)
from ..utils.errorHandler import (
    get_logger,
    ValidationError,
    ConflictError,
    NotFoundError,
)
from ..models.enums import JourneyStage
from ..services.new_schema.profile_service import get_user_profile_service


logger = get_logger(__name__)


class NewRegistrationService:
    """New registration service using the normalized schema."""
    
    def __init__(self):
        """Initialize registration service."""
        self.profile_service = get_user_profile_service()
    
    async def create_registration(
        self,
        user: User,
        registration_data: UserRegistrationRequest
    ) -> UserRegistrationResponse:
        """
        Create user registration with career details using new schema.
        
        Args:
            user: Current authenticated user
            registration_data: Registration data from request
            
        Returns:
            UserRegistrationResponse: Created registration data
            
        Raises:
            ValidationError: If validation fails
            ConflictError: If registration already exists
        """
        # Validate user type
        if registration_data.type not in ["Student", "Professional"]:
            raise ValidationError(
                message="Invalid user type",
                details={"type": registration_data.type, "allowed": ["Student", "Professional"]}
            )
        
        # Check if profile already exists for this user
        logger.info(f"Checking if profile exists for user: {user.email}")
        existing_profile = self.profile_service.get_current_profile(user.email)
        
        if existing_profile:
            # Profile exists - UPDATE it instead of creating new one
            logger.info(f"Profile already exists for user: {user.email}, updating instead of creating new")
            
            # Prepare profile data from registration request
            profile_data = self._convert_registration_to_profile_data(registration_data)
            
            # Update existing profile
            updated_profile = self.profile_service.update_profile(
                email=user.email,
                updates=profile_data
            )
            
            logger.info(f"Updated existing profile for user: {user.email}")
        else:
            # No existing profile - CREATE new one
            logger.info(f"No existing profile found for user: {user.email}, creating new one...")
            
            # Prepare profile data from registration request
            profile_data = self._convert_registration_to_profile_data(registration_data)
            
            # Create new profile
            updated_profile = self.profile_service.create_profile(
                email=user.email,
                profile_data=profile_data
            )
            
            logger.info(f"Created new profile for user: {user.email}")
        
        # Update user journey stage after successful registration
        from ..services.new_stageServices import get_stage_service
        stage_service = get_stage_service()
        
        stage_update_result = stage_service.update_user_stage(
            email=user.email,
            new_stage=JourneyStage.BASIC_REGISTERED
        )
        
        if stage_update_result.get("success"):
            logger.info(f"Updated user {user.email} stage to BASIC_REGISTERED after registration")
        else:
            logger.warning(f"Failed to update stage for user {user.email}: {stage_update_result.get('reason')}")
        
        # Return response in legacy format for API compatibility
        return self._convert_profile_to_registration_response(updated_profile, registration_data)
    
    def _convert_registration_to_profile_data(self, registration_data: UserRegistrationRequest) -> dict:
        """
        Convert registration request data to profile data format.
        
        Args:
            registration_data: Registration request data
            
        Returns:
            dict: Profile data for storage
        """
        current_info = registration_data.primary_details.current_info
        future_info = registration_data.future_info
        
        return {
            'user_type': registration_data.type,
            'career_goal': future_info.career_goal,
            'looking_for': future_info.looking_for,
            'preferred_study_destination': current_info.preferred_study_destination,
            'current_education_level': current_info.education_level,
            'field_of_study': current_info.field,
            'academic_interests': current_info.academic_interest,
            'language_preference': future_info.language_preference or 'English',
            'source': 'registration',
            'is_complete': True
        }
    
    def _convert_profile_to_registration_response(
        self, 
        profile, 
        original_registration_data: UserRegistrationRequest
    ) -> UserRegistrationResponse:
        """
        Convert profile data back to registration response format for API compatibility.
        
        Args:
            profile: UserProfile object
            original_registration_data: Original registration request data
            
        Returns:
            UserRegistrationResponse: Response in legacy format
        """
        # Reconstruct the response using the original registration data structure
        # but with profile IDs and timestamps
        return UserRegistrationResponse(
            id=profile.profile_version,  # Use profile version as ID
            u_id=profile.email,  # Use email as u_id for compatibility
            email=profile.email,
            type=profile.user_type,
            meta=MetaInfo(stage="REGISTRATION"),
            primary_details=original_registration_data.primary_details,
            future_info=original_registration_data.future_info,
            created_at=datetime.fromisoformat(profile.created_at),
            updated_at=datetime.fromisoformat(profile.updated_at)
        )
    
    async def get_registration(self, user: User) -> Optional[UserRegistrationResponse]:
        """
        Get registration for current user.
        
        Args:
            user: Current authenticated user
            
        Returns:
            UserRegistrationResponse or None
        """
        profile = self.profile_service.get_current_profile(user.email)
        
        if not profile:
            return None
        
        # Convert profile back to registration response format
        # We need to reconstruct the nested structure
        current_info = CurrentInfo(
            education_level=profile.current_education_level or "Unknown",
            field=profile.field_of_study or "Unknown",
            academic_interest=profile.academic_interests,
            preferred_study_destination=profile.preferred_study_destination
        )
        
        primary_details = PrimaryDetails(current_info=current_info)
        
        future_info = FutureInfo(
            career_goal=profile.career_goal or "Unknown",
            looking_for=profile.looking_for or "Unknown",
            language_preference=profile.language_preference
        )
        
        return UserRegistrationResponse(
            id=profile.profile_version,
            u_id=profile.email,
            email=profile.email,
            type=profile.user_type,
            meta=MetaInfo(stage="REGISTRATION"),
            primary_details=primary_details,
            future_info=future_info,
            created_at=datetime.fromisoformat(profile.created_at),
            updated_at=datetime.fromisoformat(profile.updated_at)
        )


# ============================================================================
# Service Factory Dependencies
# ============================================================================

def get_new_registration_service() -> NewRegistrationService:
    """
    Get new registration service instance.
    
    Returns:
        NewRegistrationService instance
    """
    return NewRegistrationService()
