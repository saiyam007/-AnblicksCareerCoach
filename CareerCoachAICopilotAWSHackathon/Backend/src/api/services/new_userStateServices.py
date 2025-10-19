"""
New User State Service using the normalized schema.

This service handles user journey state management using the new
normalized database schema while maintaining backward compatibility.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from ..models.enums import JourneyStage
from ..utils.errorHandler import get_logger

# Import new schema services
from .new_schema.user_service import get_new_user_service
from .new_schema.profile_service import get_user_profile_service
from .new_schema.journey_service import get_user_journey_service
from .new_schema.roadmap_service import get_new_roadmap_service
from .transformation_service import get_transformation_service

logger = get_logger(__name__)


class NewUserStateService:
    """Service for managing user journey state using new schema."""
    
    def __init__(self):
        """Initialize with new schema services."""
        self.user_service = get_new_user_service()
        self.profile_service = get_user_profile_service()
        self.journey_service = get_user_journey_service()
        self.roadmap_service = get_new_roadmap_service()
        self.transformation_service = get_transformation_service()
    
    def get_journey_state(self, email: str) -> Dict[str, Any]:
        """
        Get complete journey state for user using new schema.
        
        Args:
            email: User email address
            
        Returns:
            Dict: Complete journey state information
        """
        try:
            # Get user from new schema
            user = self.user_service.get_user(email)
            if not user:
                logger.warning(f"User not found: {email}")
                return self._create_default_state(email)
            
            # Get current profile
            profile = self.profile_service.get_current_profile(email)
            
            # Get current journey
            journey = self.journey_service.get_active_journey(email)
            if not journey:
                # Create journey if it doesn't exist
                journey = self.journey_service.create_journey(email)
            
            # Get latest roadmap
            latest_roadmap = self.roadmap_service.get_latest_roadmap(email)
            
            # Combine user data for transformation
            combined_user_data = {
                **user.to_dict(),
                'profile': profile.to_dict() if profile else None,
                'journey': journey.to_dict() if journey else None
            }
            
            # Transform to legacy format for backward compatibility
            legacy_user_data = self.transformation_service.transform_user_to_legacy_format(
                combined_user_data
            )
            
            # Get stage info
            stage_info = self._get_stage_info(journey.current_stage)
            
            # Get progress information
            progress = self._get_progress_info(journey)
            
            # Get current data based on stage
            current_data = self._get_current_data_for_stage(
                journey.current_stage, 
                latest_roadmap, 
                profile
            )
            
            # Get next actions
            next_actions = self._get_next_actions(journey.current_stage)
            
            return {
                "user": legacy_user_data,
                "journey_stage": journey.current_stage,
                "stage_info": stage_info,
                "progress": progress,
                "current_data": current_data,
                "next_actions": next_actions
            }
            
        except Exception as e:
            logger.error(f"Error getting journey state for {email}: {e}")
            return self._create_default_state(email)
    
    def _create_default_state(self, email: str) -> Dict[str, Any]:
        """Create default state for new user."""
        return {
            "user": {
                "email": email,
                "journey_stage": JourneyStage.AUTHENTICATED.value
            },
            "journey_stage": JourneyStage.AUTHENTICATED.value,
            "stage_info": self._get_stage_info(JourneyStage.AUTHENTICATED.value),
            "progress": {
                "current_step": 1,
                "total_steps": 7,
                "progress_percentage": 14.3,
                "completed_steps": [JourneyStage.AUTHENTICATED.value]
            },
            "current_data": {
                "registration": None,
                "questions": None,
                "answers": None,
                "roadmap": None,
                "roadmap_id": None
            },
            "next_actions": self._get_next_actions(JourneyStage.AUTHENTICATED.value)
        }
    
    def _get_stage_info(self, stage: str) -> Dict[str, Any]:
        """Get stage information."""
        stage_order = {
            JourneyStage.AUTHENTICATED: 1,
            JourneyStage.BASIC_REGISTERED: 2,
            JourneyStage.PROFILE_COMPLETED: 3,
            JourneyStage.CAREER_PATHS_GENERATED: 4,
            JourneyStage.CAREER_PATH_SELECTED: 5,
            JourneyStage.ROADMAP_GENERATED: 6,
            JourneyStage.ROADMAP_ACTIVE: 7,
            JourneyStage.JOURNEY_COMPLETED: 8,
            JourneyStage.JOURNEY_PAUSED: 9
        }
        
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
        
        return {
            "stage": stage,
            "order": stage_order.get(stage, 0),
            "description": stage_descriptions.get(stage, "Unknown stage"),
            "is_valid": stage in stage_order
        }
    
    def _get_progress_info(self, journey) -> Dict[str, Any]:
        """Get progress information from journey."""
        stage_order = {
            JourneyStage.AUTHENTICATED: 1,
            JourneyStage.BASIC_REGISTERED: 2,
            JourneyStage.PROFILE_COMPLETED: 3,
            JourneyStage.CAREER_PATHS_GENERATED: 4,
            JourneyStage.CAREER_PATH_SELECTED: 5,
            JourneyStage.ROADMAP_GENERATED: 6,
            JourneyStage.ROADMAP_ACTIVE: 7,
            JourneyStage.JOURNEY_COMPLETED: 8,
            JourneyStage.JOURNEY_PAUSED: 9
        }
        
        current_order = stage_order.get(journey.current_stage, 1)
        total_steps = 7  # Main journey steps (excluding special states)
        
        # Calculate completed steps
        completed_steps = []
        for stage, order in stage_order.items():
            if order <= current_order and order <= total_steps:
                completed_steps.append(stage.value)
        
        progress_percentage = (current_order / total_steps) * 100
        
        return {
            "current_step": current_order,
            "total_steps": total_steps,
            "progress_percentage": progress_percentage,
            "completed_steps": completed_steps
        }
    
    def _get_current_data_for_stage(self, current_stage: str, latest_roadmap: Optional[Dict], profile: Optional[Any]) -> Dict[str, Any]:
        """Get current data based on journey stage."""
        current_data = {
            "registration": None,
            "questions": None,
            "answers": None,
            "roadmap": None,
            "roadmap_id": None
        }
        
        # Add registration data if profile exists
        if profile:
            # Use profile data as registration data (they're similar in our schema)
            current_data["registration"] = profile.to_dict() if profile else None
        
        # Add roadmap data based on stage
        if current_stage in [JourneyStage.CAREER_PATHS_GENERATED.value, JourneyStage.ROADMAP_GENERATED.value]:
            if latest_roadmap:
                current_data["roadmap_id"] = latest_roadmap.roadmap_id
                
                # Add answers and roadmap if available
                if hasattr(latest_roadmap, 'answers') and latest_roadmap.answers:
                    current_data["answers"] = latest_roadmap.answers
                if hasattr(latest_roadmap, 'career_paths') and latest_roadmap.career_paths:
                    current_data["roadmap"] = latest_roadmap.career_paths
        
        # Add questions if available
        if latest_roadmap and hasattr(latest_roadmap, 'questions') and latest_roadmap.questions:
            current_data["questions"] = latest_roadmap.questions
        
        return current_data
    
    def _get_next_actions(self, current_stage: str) -> List[Dict[str, Any]]:
        """Get next available actions based on current stage."""
        actions = []
        
        if current_stage == JourneyStage.AUTHENTICATED.value:
            actions.append({
                "action": "complete_registration",
                "title": "Complete Registration",
                "description": "Provide your career details",
                "endpoint": "/v1/registration/",
                "method": "POST",
                "requires_data": True
            })
        
        elif current_stage == JourneyStage.BASIC_REGISTERED.value:
            actions.append({
                "action": "generate_questions",
                "title": "Generate Questions",
                "description": "Get personalized career questions",
                "endpoint": "/v1/ai/profile/questions",
                "method": "POST",
                "requires_data": False
            })
            actions.append({
                "action": "update_registration",
                "title": "Update Registration",
                "description": "Modify your career details (will reset questions)",
                "endpoint": "/v1/registration/",
                "method": "POST",
                "requires_data": True
            })
        
        elif current_stage == JourneyStage.PROFILE_COMPLETED.value:
            actions.append({
                "action": "answer_questions",
                "title": "Answer Questions",
                "description": "Answer the generated career questions",
                "endpoint": "/v1/ai/profile/roadmap",
                "method": "POST",
                "requires_data": True
            })
            actions.append({
                "action": "regenerate_questions",
                "title": "Regenerate Questions",
                "description": "Generate new career questions",
                "endpoint": "/v1/ai/profile/questions",
                "method": "POST",
                "requires_data": False
            })
        
        elif current_stage == JourneyStage.CAREER_PATHS_GENERATED.value:
            actions.append({
                "action": "select_career_path",
                "title": "Select Career Path",
                "description": "Choose your preferred career path",
                "endpoint": "/v1/ai/profile/detailed-roadmap",
                "method": "POST",
                "requires_data": True
            })
            actions.append({
                "action": "regenerate_roadmap",
                "title": "Regenerate Roadmap",
                "description": "Generate new career paths",
                "endpoint": "/v1/ai/profile/roadmap",
                "method": "POST",
                "requires_data": True
            })
        
        elif current_stage == JourneyStage.CAREER_PATH_SELECTED.value:
            actions.append({
                "action": "view_detailed_roadmap",
                "title": "View Detailed Roadmap",
                "description": "View your comprehensive career roadmap",
                "endpoint": "/v1/ai/profile/detailed-roadmap",
                "method": "POST",
                "requires_data": True
            })
        
        elif current_stage == JourneyStage.ROADMAP_GENERATED.value:
            actions.append({
                "action": "start_journey",
                "title": "Start Journey",
                "description": "Begin your career development journey",
                "endpoint": "/v1/journey/start",
                "method": "POST",
                "requires_data": False
            })
            actions.append({
                "action": "view_roadmap",
                "title": "View Roadmap",
                "description": "Review your detailed roadmap",
                "endpoint": "/v1/roadmap/current",
                "method": "GET",
                "requires_data": False
            })
        
        elif current_stage == JourneyStage.ROADMAP_ACTIVE.value:
            actions.append({
                "action": "track_progress",
                "title": "Track Progress",
                "description": "Update your learning progress",
                "endpoint": "/v1/journey/progress",
                "method": "PUT",
                "requires_data": True
            })
            actions.append({
                "action": "pause_journey",
                "title": "Pause Journey",
                "description": "Temporarily pause your journey",
                "endpoint": "/v1/journey/pause",
                "method": "POST",
                "requires_data": False
            })
        
        elif current_stage == JourneyStage.JOURNEY_PAUSED.value:
            actions.append({
                "action": "resume_journey",
                "title": "Resume Journey",
                "description": "Continue your career development journey",
                "endpoint": "/v1/journey/resume",
                "method": "POST",
                "requires_data": False
            })
        
        elif current_stage == JourneyStage.JOURNEY_COMPLETED.value:
            actions.append({
                "action": "view_certificate",
                "title": "View Certificate",
                "description": "Download your completion certificate",
                "endpoint": "/v1/journey/certificate",
                "method": "GET",
                "requires_data": False
            })
            actions.append({
                "action": "start_new_journey",
                "title": "Start New Journey",
                "description": "Begin a new career development journey",
                "endpoint": "/v1/journey/new",
                "method": "POST",
                "requires_data": True
            })
        
        return actions


# ============================================================================
# Service Factory Dependencies
# ============================================================================

def get_user_state_service() -> NewUserStateService:
    """
    Get user state service instance using new schema.
    
    Returns:
        NewUserStateService instance
    """
    return NewUserStateService()
