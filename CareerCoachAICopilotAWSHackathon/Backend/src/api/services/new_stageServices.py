"""
New Stage Management Service using the normalized schema.

Handles stage transitions, validation, and persistence for user journey stages
using the new normalized database schema.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from ..models.enums import JourneyStage
from ..utils.errorHandler import get_logger

# Import new schema services
from .new_schema.journey_service import get_user_journey_service
from .new_schema.user_service import get_new_user_service

logger = get_logger(__name__)


class NewStageService:
    """Service for managing user journey stages using new schema."""
    
    def __init__(self):
        """Initialize with new schema services."""
        self.journey_service = get_user_journey_service()
        self.user_service = get_new_user_service()
        
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
        Get current journey stage for a user using new schema.
        
        Args:
            email: User's email address
            
        Returns:
            Current stage string or None if user not found
        """
        try:
            journey = self.journey_service.get_active_journey(email)
            if journey:
                return journey.current_stage
            return None
        except Exception as e:
            logger.error(f"Error getting user stage for {email}: {str(e)}")
            return None
    
    def validate_stage_transition(self, current_stage: str, new_stage: str) -> Dict[str, Any]:
        """
        Validate if stage transition is allowed.
        
        Args:
            current_stage: Current journey stage
            new_stage: Target journey stage
            
        Returns:
            Dict with validation result and details
        """
        try:
            # Same stage is always valid
            if current_stage == new_stage:
                return {
                    "valid": True,
                    "reason": "Same stage",
                    "transition_type": "none"
                }
            
            # Get stage order numbers
            current_order = self.STAGE_ORDER.get(current_stage, 0)
            new_order = self.STAGE_ORDER.get(new_stage, 0)
            
            # Handle special cases
            if current_stage == JourneyStage.ROADMAP_ACTIVE.value:
                # From ROADMAP_ACTIVE, can only go to JOURNEY_COMPLETED or JOURNEY_PAUSED
                if new_stage in [JourneyStage.JOURNEY_COMPLETED.value, JourneyStage.JOURNEY_PAUSED.value]:
                    return {
                        "valid": True,
                        "reason": "Valid transition from ROADMAP_ACTIVE",
                        "transition_type": "special"
                    }
                else:
                    return {
                        "valid": False,
                        "reason": f"Cannot transition from {current_stage} to {new_stage}",
                        "transition_type": "invalid"
                    }
            
            if current_stage == JourneyStage.JOURNEY_PAUSED.value:
                # From JOURNEY_PAUSED, can only go back to ROADMAP_ACTIVE
                if new_stage == JourneyStage.ROADMAP_ACTIVE.value:
                    return {
                        "valid": True,
                        "reason": "Resuming from pause",
                        "transition_type": "resume"
                    }
                else:
                    return {
                        "valid": False,
                        "reason": f"Cannot transition from {current_stage} to {new_stage}",
                        "transition_type": "invalid"
                    }
            
            # Normal forward progression
            if new_order > current_order:
                return {
                    "valid": True,
                    "reason": "Forward progression",
                    "transition_type": "forward"
                }
            
            # Backward progression (not allowed in normal flow)
            if new_order < current_order:
                return {
                    "valid": False,
                    "reason": f"Cannot go backward from {current_stage} to {new_stage}",
                    "transition_type": "backward"
                }
            
            return {
                "valid": False,
                "reason": "Unknown stage transition",
                "transition_type": "unknown"
            }
            
        except Exception as e:
            logger.error(f"Error validating stage transition: {e}")
            return {
                "valid": False,
                "reason": f"Validation error: {str(e)}",
                "transition_type": "error"
            }
    
    def update_user_stage(self, email: str, new_stage: str) -> Dict[str, Any]:
        """
        Update user's journey stage using new schema.
        
        Args:
            email: User's email address
            new_stage: New journey stage
            
        Returns:
            Dict with update result
        """
        try:
            # Get current stage
            current_stage = self.get_user_stage(email)
            if not current_stage:
                current_stage = JourneyStage.AUTHENTICATED.value
            
            # Validate transition
            validation = self.validate_stage_transition(current_stage, new_stage)
            if not validation["valid"]:
                return {
                    "success": False,
                    "reason": validation["reason"],
                    "current_stage": current_stage,
                    "target_stage": new_stage
                }
            
            # Update journey in new schema
            journey = self.journey_service.get_active_journey(email)
            if not journey:
                # Create journey if it doesn't exist
                journey = self.journey_service.create_journey(email)
            
            # Update stage
            updated_journey = self.journey_service.update_journey(
                email, 
                {'current_stage': new_stage}
            )
            
            if updated_journey:
                logger.info(f"Updated user {email} stage from {current_stage} to {new_stage}")
                return {
                    "success": True,
                    "reason": "Stage updated successfully",
                    "current_stage": new_stage,
                    "previous_stage": current_stage,
                    "transition_type": validation["transition_type"]
                }
            else:
                return {
                    "success": False,
                    "reason": "Failed to update journey stage",
                    "current_stage": current_stage,
                    "target_stage": new_stage
                }
                
        except Exception as e:
            logger.error(f"Error updating user stage for {email}: {e}")
            return {
                "success": False,
                "reason": f"Update error: {str(e)}",
                "current_stage": current_stage if 'current_stage' in locals() else None,
                "target_stage": new_stage
            }
    
    def get_stage_info(self, stage: str) -> Dict[str, Any]:
        """
        Get information about a specific stage.
        
        Args:
            stage: Journey stage
            
        Returns:
            Dict with stage information
        """
        stage_order = self.STAGE_ORDER.get(stage, 0)
        
        stage_info = {
            "stage": stage,
            "order": stage_order,
            "is_valid": stage_order > 0
        }
        
        # Add descriptions for each stage
        stage_descriptions = {
            JourneyStage.AUTHENTICATED: "User has authenticated via Google",
            JourneyStage.BASIC_REGISTERED: "User has completed basic registration",
            JourneyStage.PROFILE_COMPLETED: "User profile is complete",
            JourneyStage.CAREER_PATHS_GENERATED: "Career paths are available - user needs to select one",
            JourneyStage.CAREER_PATH_SELECTED: "Career path chosen - needs roadmap generation",
            JourneyStage.ROADMAP_GENERATED: "Roadmap ready - user can start journey",
            JourneyStage.ROADMAP_ACTIVE: "User is actively following the roadmap",
            JourneyStage.JOURNEY_COMPLETED: "User has completed their career journey",
            JourneyStage.JOURNEY_PAUSED: "User has paused their journey"
        }
        
        stage_info["description"] = stage_descriptions.get(stage, "Unknown stage")
        
        return stage_info
    
    def get_journey_progress(self, email: str) -> Dict[str, Any]:
        """
        Get detailed journey progress for a user.
        
        Args:
            email: User's email address
            
        Returns:
            Dict with progress information
        """
        try:
            journey = self.journey_service.get_active_journey(email)
            if not journey:
                return {
                    "current_step": 0,
                    "total_steps": len(self.STAGE_ORDER),
                    "progress_percentage": 0.0,
                    "completed_steps": [],
                    "current_stage": JourneyStage.AUTHENTICATED.value
                }
            
            current_order = self.STAGE_ORDER.get(journey.current_stage, 0)
            total_steps = len(self.STAGE_ORDER)
            
            # Calculate completed steps
            completed_steps = []
            for stage, order in self.STAGE_ORDER.items():
                if order <= current_order:
                    completed_steps.append(stage.value)
            
            progress_percentage = (current_order / total_steps) * 100
            
            return {
                "current_step": current_order,
                "total_steps": total_steps,
                "progress_percentage": progress_percentage,
                "completed_steps": completed_steps,
                "current_stage": journey.current_stage
            }
            
        except Exception as e:
            logger.error(f"Error getting journey progress for {email}: {e}")
            return {
                "current_step": 0,
                "total_steps": len(self.STAGE_ORDER),
                "progress_percentage": 0.0,
                "completed_steps": [],
                "current_stage": JourneyStage.AUTHENTICATED.value
            }


# ============================================================================
# Service Factory Dependencies
# ============================================================================

def get_stage_service() -> NewStageService:
    """
    Get stage service instance using new schema.
    
    Returns:
        NewStageService instance
    """
    return NewStageService()
