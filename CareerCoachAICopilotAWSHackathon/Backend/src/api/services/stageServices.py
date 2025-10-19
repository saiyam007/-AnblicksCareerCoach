"""
Stage Management Service for user journey tracking.

Handles stage transitions, validation, and persistence for user journey stages.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from ..models.enums import JourneyStage
from ..core.dynamodbUsersClient import DynamoDBUsersClient
from ..utils.apiHelper import get_logger

logger = get_logger(__name__)


class StageService:
    """Service for managing user journey stages."""
    
    def __init__(self):
        self.db_client = DynamoDBUsersClient()
        
        # Define stage order for validation (higher number = later stage)
        self.STAGE_ORDER = {
            JourneyStage.AUTHENTICATED: 1,
            JourneyStage.BASIC_REGISTERED: 2,
            JourneyStage.PROFILE_COMPLETED: 3,
            JourneyStage.CAREER_PATHS_GENERATED: 4,
            JourneyStage.CAREER_PATH_SELECTED: 5,
            JourneyStage.ROADMAP_GENERATED: 6,
            JourneyStage.ROADMAP_ACTIVE: 7,
            JourneyStage.JOURNEY_COMPLETED: 8,
            JourneyStage.JOURNEY_PAUSED: 9  # Special case - can only go to/from ROADMAP_ACTIVE
        }
    
    def get_user_stage(self, email: str) -> Optional[str]:
        """
        Get current journey stage for a user.
        
        Args:
            email: User's email address
            
        Returns:
            Current stage string or None if user not found
        """
        try:
            user_data = self.db_client.get_user_profile(email)
            if user_data:
                return user_data.get("journey_stage", JourneyStage.AUTHENTICATED)
            return None
        except Exception as e:
            logger.error(f"Error getting user stage for {email}: {str(e)}")
            return None
    
    def validate_stage_transition(self, current_stage: str, new_stage: str) -> Dict[str, Any]:
        """
        Validate if a stage transition is allowed.
        
        Args:
            current_stage: Current stage
            new_stage: Proposed new stage
            
        Returns:
            Validation result with success flag and reason
        """
        # Same stage - allowed (no change)
        if current_stage == new_stage:
            return {
                "valid": True,
                "reason": "Same stage - no change needed"
            }
        
        # Handle special pause/resume case
        if (current_stage == JourneyStage.ROADMAP_ACTIVE and new_stage == JourneyStage.JOURNEY_PAUSED) or \
           (current_stage == JourneyStage.JOURNEY_PAUSED and new_stage == JourneyStage.ROADMAP_ACTIVE):
            return {
                "valid": True,
                "reason": "Valid pause/resume transition"
            }
        
        # Check if both stages exist in our order mapping
        if current_stage not in self.STAGE_ORDER or new_stage not in self.STAGE_ORDER:
            return {
                "valid": False,
                "reason": f"Invalid stage: {current_stage} or {new_stage}"
            }
        
        # Check if it's a forward progression (no regression allowed)
        current_order = self.STAGE_ORDER[current_stage]
        new_order = self.STAGE_ORDER[new_stage]
        
        if new_order < current_order:
            return {
                "valid": False,
                "reason": f"Cannot regress from {current_stage} to {new_stage}"
            }
        
        return {
            "valid": True,
            "reason": "Valid forward progression"
        }
    
    def update_user_stage(self, email: str, new_stage: str, force_update: bool = False) -> Dict[str, Any]:
        """
        Update user's journey stage with validation.
        
        Args:
            email: User's email address
            new_stage: New stage to set
            force_update: Force update even if validation fails (admin use)
            
        Returns:
            Update result with success flag and details
        """
        try:
            # Get current stage
            current_stage = self.get_user_stage(email)
            
            if current_stage is None:
                # User not found - set default stage for new user
                current_stage = JourneyStage.AUTHENTICATED
                logger.info(f"User {email} not found, setting default stage: {current_stage}")
            
            # Validate transition unless forced
            if not force_update:
                validation = self.validate_stage_transition(current_stage, new_stage)
                if not validation["valid"]:
                    logger.warning(f"Invalid stage transition for {email}: {validation['reason']}")
                    return {
                        "success": False,
                        "reason": validation["reason"],
                        "current_stage": current_stage,
                        "attempted_stage": new_stage
                    }
            
            # Skip update if same stage
            if current_stage == new_stage:
                logger.info(f"User {email} already at stage {new_stage}, skipping update")
                return {
                    "success": True,
                    "message": "Stage unchanged",
                    "current_stage": current_stage,
                    "new_stage": new_stage
                }
            
            # Get current user data and update stage
            user_data = self.db_client.get_user_profile(email)
            if not user_data:
                logger.error(f"User {email} not found for stage update")
                return {
                    "success": False,
                    "reason": "User not found",
                    "error": "Cannot update stage for non-existent user"
                }
            
            # Update the journey_stage field
            user_data["journey_stage"] = new_stage
            
            # Save updated user data
            self.db_client.upsert_user_profile(user_data)
            
            logger.info(f"Successfully updated user {email} stage: {current_stage} -> {new_stage}")
            return {
                "success": True,
                "message": "Stage updated successfully",
                "previous_stage": current_stage,
                "current_stage": new_stage,
                "updated_at": datetime.utcnow().isoformat()
            }
                
        except Exception as e:
            logger.exception(f"Error updating stage for user {email}: {str(e)}")
            return {
                "success": False,
                "reason": "Unexpected error",
                "error": str(e)
            }
    
    def get_stage_info(self, stage: str) -> Dict[str, Any]:
        """
        Get information about a specific stage.
        
        Args:
            stage: Stage name
            
        Returns:
            Stage information including order and description
        """
        stage_descriptions = {
            JourneyStage.AUTHENTICATED: "First time login - needs basic registration",
            JourneyStage.BASIC_REGISTERED: "Basic details saved - needs AI profile completion",
            JourneyStage.PROFILE_COMPLETED: "AI profile done - needs career paths generation",
            JourneyStage.CAREER_PATHS_GENERATED: "Paths available - user needs to select one",
            JourneyStage.CAREER_PATH_SELECTED: "Path chosen - needs roadmap generation",
            JourneyStage.ROADMAP_GENERATED: "Roadmap ready - user can start journey",
            JourneyStage.ROADMAP_ACTIVE: "Journey in progress",
            JourneyStage.JOURNEY_COMPLETED: "Full journey completed",
            JourneyStage.JOURNEY_PAUSED: "User paused but can resume"
        }
        
        return {
            "stage": stage,
            "order": self.STAGE_ORDER.get(stage, 0),
            "description": stage_descriptions.get(stage, "Unknown stage"),
            "is_valid": stage in self.STAGE_ORDER
        }


# Service instance
_stage_service = None

def get_stage_service() -> StageService:
    """Get or create stage service instance."""
    global _stage_service
    if _stage_service is None:
        _stage_service = StageService()
    return _stage_service
