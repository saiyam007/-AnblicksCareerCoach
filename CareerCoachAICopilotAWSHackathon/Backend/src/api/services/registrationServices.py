"""
Business logic services for user registration.
Contains RegistrationService for handling career registration data.
"""

from datetime import datetime
from typing import Optional
from fastapi import Depends

from ..models.registrationModel import Registration
from ..models.userModel import User
from ..utils.database import get_db
from ..schemas import (
    UserRegistrationRequest,
    UserRegistrationResponse,
    MetaInfo,
)
from ..utils.errorHandler import (
    get_logger,
    ValidationError,
    ConflictError,
    NotFoundError,
)
from ..models.enums import JourneyStage


logger = get_logger(__name__)


# ============================================================================
# Registration Service
# ============================================================================

class RegistrationService:
    """Registration service for handling career registration data."""
    
    def __init__(self, db_table=None):
        """
        Initialize registration service.
        
        Args:
            db_table: DynamoDB table (not used but kept for compatibility)
        """
        self.db_table = db_table
    
    async def create_registration(
        self,
        user: User,
        registration_data: UserRegistrationRequest
    ) -> UserRegistrationResponse:
        """
        Create user registration with career details.
        
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
        
        # Check if registration already exists for this user
        logger.info(f"Checking if registration exists for u_id: {user.id}")
        existing_registration = await Registration.get_by_u_id(user.id)
        
        if existing_registration:
            # Registration exists - UPDATE it instead of creating new one
            logger.info(f"Registration already exists for u_id: {user.id}, updating instead of creating new")
            
            # Reuse the existing ID to prevent duplicates
            registration = Registration(
                id=existing_registration.id,  #  Reuse existing ID
                u_id=user.id,
                email=user.email,
                type=registration_data.type,
                meta={'stage': 'REGISTRATION'},
                primary_details={
                    'current_info': registration_data.primary_details.current_info.model_dump()
                },
                future_info=registration_data.future_info.model_dump(),
                created_at=existing_registration.created_at  # Keep original creation time
            )
            
            logger.info(f"Updating existing registration id: {registration.id}")
        else:
            # No existing registration - CREATE new one
            logger.info(f"No existing registration found for u_id: {user.id}, creating new one...")
            
            # Create registration object
            registration = Registration(
                u_id=user.id,  # User ID from authenticated user
                email=user.email,  # Email from authenticated user
                type=registration_data.type,
                meta={'stage': 'REGISTRATION'},
                primary_details={
                    'current_info': registration_data.primary_details.current_info.model_dump()
                },
                future_info=registration_data.future_info.model_dump()
            )
        
        # Save to DynamoDB
        try:
            await registration.save()
            logger.info(f"Registration created for user: {user.email} (u_id: {user.id})")
        except Exception as e:
            logger.error(f"Error creating registration: {str(e)}", exc_info=True)
            raise ValidationError(
                message="Failed to create registration",
                details={"error": str(e)}
            )
        
        # Update user journey stage after successful registration
        from ..services.stageServices import get_stage_service
        stage_service = get_stage_service()
        
        stage_update_result = stage_service.update_user_stage(
            email=user.email,
            new_stage=JourneyStage.BASIC_REGISTERED
        )
        
        if stage_update_result.get("success"):
            logger.info(f"Updated user {user.email} stage to BASIC_REGISTERED after registration")
        else:
            logger.warning(f"Failed to update stage for user {user.email}: {stage_update_result.get('reason')}")
        
        # Return response
        return UserRegistrationResponse(
            id=registration.id,
            u_id=registration.u_id,
            email=registration.email,
            type=registration.type,
            meta=MetaInfo(**registration.meta),
            primary_details=registration_data.primary_details,
            future_info=registration_data.future_info,
            created_at=datetime.fromisoformat(registration.created_at),
            updated_at=datetime.fromisoformat(registration.updated_at)
        )
    
    async def get_registration(self, user: User) -> Optional[UserRegistrationResponse]:
        """
        Get registration for current user.
        
        Args:
            user: Current authenticated user
            
        Returns:
            UserRegistrationResponse or None
        """
        registration = await Registration.get_by_u_id(user.id)
        
        if not registration:
            return None
        
        # Convert to response model
        from ..schemas import PrimaryDetails, CurrentInfo, FutureInfo
        
        return UserRegistrationResponse(
            id=registration.id,
            u_id=registration.u_id,
            email=registration.email,
            type=registration.type,
            meta=MetaInfo(**registration.meta),
            primary_details=PrimaryDetails(
                current_info=CurrentInfo(**registration.primary_details.get('current_info', {}))
            ),
            future_info=FutureInfo(**registration.future_info),
            created_at=datetime.fromisoformat(registration.created_at),
            updated_at=datetime.fromisoformat(registration.updated_at)
        )
    


# ============================================================================
# Service Factory Dependencies
# ============================================================================

def get_registration_service(db_table = Depends(get_db)) -> RegistrationService:
    """
    Get registration service instance.
    
    Args:
        db_table: DynamoDB table
        
    Returns:
        RegistrationService instance
    """
    return RegistrationService(db_table)

