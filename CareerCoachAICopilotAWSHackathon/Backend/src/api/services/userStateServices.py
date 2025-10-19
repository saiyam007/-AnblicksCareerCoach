"""
User Journey State Service.

Business logic for comprehensive user journey state management:
- Complete state retrieval with all stage-specific data
- Progress tracking and next actions
- Frontend-ready state preparation
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from ..models.userModel import User
from ..schemas.userState import (
    UserJourneyState,
    StageInfo,
    ProgressInfo,
    NextAction,
    CurrentData
)
from ..schemas.auth import UserResponse
from ..schemas.registration import UserRegistrationResponse
from ..models.enums import JourneyStage
from ..services.new_stageServices import get_stage_service
from ..services.new_schema.user_service import get_new_user_service
from ..services.new_schema.profile_service import get_user_profile_service
from ..services.new_schema.roadmap_service import get_new_roadmap_service
from ..utils.errorHandler import get_logger

logger = get_logger(__name__)


class UserStateService:
    """Service for managing comprehensive user journey state."""
    
    def __init__(self):
        """Initialize user state service."""
        self.stage_service = get_stage_service()
        self.user_service = get_new_user_service()
        self.profile_service = get_user_profile_service()
        self.roadmap_service = get_new_roadmap_service()
        
        # Define total steps in journey
        self.total_steps = 7
        
        # Define stage order mapping
        self.stage_order = {
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
    
    async def get_user_journey_state(self, user: User) -> UserJourneyState:
        """
        Get complete user journey state with all available data.
        
        Args:
            user: Current authenticated user
            
        Returns:
            Complete user journey state
        """
        try:
            logger.info(f"Getting journey state for user: {user.email}")
            
            # Get current journey stage
            current_stage = self.stage_service.get_user_stage(user.email) or JourneyStage.AUTHENTICATED
            
            # Get stage information
            stage_info = self.stage_service.get_stage_info(current_stage)
            
            # Get progress information
            progress = self._calculate_progress(current_stage)
            
            # Get current data based on stage
            current_data = await self._get_current_data(user, current_stage)
            
            # Get next available actions
            next_actions = self._get_next_actions(current_stage)
            
            # Create user response
            user_response = UserResponse.model_validate(user.to_dict())
            user_response.journey_stage = current_stage
            
            # Build complete state
            journey_state = UserJourneyState(
                user=user_response,
                journey_stage=current_stage,
                stage_info=StageInfo(**stage_info),
                progress=progress,
                current_data=current_data,
                next_actions=next_actions
            )
            
            logger.info(f"Retrieved complete journey state for user: {user.email}")
            return journey_state
            
        except Exception as e:
            logger.error(f"Error getting journey state for user {user.email}: {e}")
            raise
    
    def _calculate_progress(self, current_stage: str) -> ProgressInfo:
        """
        Calculate user progress based on current stage.
        
        Args:
            current_stage: Current journey stage
            
        Returns:
            Progress information
        """
        current_step = self.stage_order.get(current_stage, 1)
        progress_percentage = (current_step / self.total_steps) * 100
        
        # Get completed steps (stages before current)
        completed_steps = []
        for stage, order in self.stage_order.items():
            if order < current_step:
                completed_steps.append(stage)
        
        return ProgressInfo(
            current_step=current_step,
            total_steps=self.total_steps,
            progress_percentage=round(progress_percentage, 1),
            completed_steps=completed_steps
        )
    
    async def _get_current_data(self, user: User, current_stage: str) -> CurrentData:
        """
        Get current data available to user based on journey stage.
        
        Args:
            user: Current authenticated user
            current_stage: Current journey stage
            
        Returns:
            Current available data
        """
        current_data = CurrentData()
        
        try:
            # Get registration data for stages that have it
            if current_stage in [JourneyStage.BASIC_REGISTERED, JourneyStage.PROFILE_COMPLETED, 
                               JourneyStage.CAREER_PATHS_GENERATED, JourneyStage.ROADMAP_GENERATED]:
                try:
                    registration = await self.registration_service.get_registration(user)
                    if registration:
                        current_data.registration = registration
                except Exception as e:
                    logger.warning(f"Could not get registration data for user {user.email}: {e}")
            
            # Get questions and roadmap data for later stages
            if current_stage in [JourneyStage.CAREER_PATHS_GENERATED, JourneyStage.ROADMAP_GENERATED]:
                try:
                    latest_roadmap = self.roadmap_service.get_latest_roadmap(user.email)
                    if latest_roadmap:
                        current_data.roadmap_id = latest_roadmap.get("roadmapId")
                        
                        # Get questions if available
                        if "questions" in latest_roadmap:
                            current_data.questions = latest_roadmap["questions"]
                        
                        # Get answers and roadmap if available (for CAREER_PATHS_GENERATED and ROADMAP_GENERATED stages)
                        if current_stage in [JourneyStage.CAREER_PATHS_GENERATED, JourneyStage.ROADMAP_GENERATED]:
                            if "answers" in latest_roadmap:
                                current_data.answers = latest_roadmap["answers"]
                            if "roadmap" in latest_roadmap:
                                current_data.roadmap = latest_roadmap["roadmap"]
                            if "selectedCareerPath" in latest_roadmap:
                                current_data.selected_career_path = latest_roadmap["selectedCareerPath"]
                except Exception as e:
                    logger.warning(f"Could not get roadmap data for user {user.email}: {e}")
            
            return current_data
            
        except Exception as e:
            logger.error(f"Error getting current data for user {user.email}: {e}")
            return current_data
    
    def _get_next_actions(self, current_stage: str) -> List[NextAction]:
        """
        Get next available actions based on current stage.
        
        Args:
            current_stage: Current journey stage
            
        Returns:
            List of available next actions
        """
        actions = []
        
        if current_stage == JourneyStage.AUTHENTICATED:
            actions.append(NextAction(
                action="complete_registration",
                title="Complete Registration",
                description="Fill out your career details and goals",
                endpoint="/v1/registration/",
                method="POST",
                requires_data=True
            ))
        
        elif current_stage == JourneyStage.BASIC_REGISTERED:
            actions.append(NextAction(
                action="complete_ai_profile",
                title="Complete AI Profile",
                description="Generate AI-powered profile summary",
                endpoint="/v1/ai/user/complete-profile",
                method="POST",
                requires_data=True
            ))
            actions.append(NextAction(
                action="update_registration",
                title="Update Registration",
                description="Modify your career details",
                endpoint="/v1/registration/",
                method="POST",
                requires_data=True
            ))
        
        elif current_stage == JourneyStage.PROFILE_COMPLETED:
            actions.append(NextAction(
                action="generate_questions",
                title="Generate Questions",
                description="Generate personalized career questions",
                endpoint="/v1/ai/profile/questions",
                method="POST",
                requires_data=False
            ))
            actions.append(NextAction(
                action="update_registration",
                title="Update Registration",
                description="Modify your career details",
                endpoint="/v1/registration/",
                method="POST",
                requires_data=True
            ))
        
        elif current_stage == JourneyStage.CAREER_PATHS_GENERATED:
            actions.append(NextAction(
                action="answer_questions",
                title="Answer Questions",
                description="Answer the generated career questions",
                endpoint="/v1/ai/profile/roadmap",
                method="POST",
                requires_data=True
            ))
            actions.append(NextAction(
                action="regenerate_questions",
                title="Regenerate Questions",
                description="Generate new career questions",
                endpoint="/v1/ai/profile/questions",
                method="POST",
                requires_data=False
            ))
            actions.append(NextAction(
                action="update_registration",
                title="Update Registration",
                description="Modify your career details (will reset questions)",
                endpoint="/v1/registration/",
                method="PUT",
                requires_data=True
            ))
        
        elif current_stage == JourneyStage.ROADMAP_GENERATED:
            actions.append(NextAction(
                action="select_career_path",
                title="Select Career Path",
                description="Choose your preferred career path",
                endpoint="/v1/roadmap/select-path",
                method="POST",
                requires_data=True
            ))
            actions.append(NextAction(
                action="regenerate_roadmap",
                title="Regenerate Roadmap",
                description="Answer questions again to generate new roadmap",
                endpoint="/v1/ai/profile/roadmap",
                method="POST",
                requires_data=True
            ))
            actions.append(NextAction(
                action="update_registration",
                title="Update Registration",
                description="Modify your career details (will reset roadmap)",
                endpoint="/v1/registration/",
                method="PUT",
                requires_data=True
            ))
        
        elif current_stage in [JourneyStage.ROADMAP_ACTIVE, JourneyStage.JOURNEY_COMPLETED, JourneyStage.JOURNEY_PAUSED]:
            actions.append(NextAction(
                action="view_roadmap",
                title="View Roadmap",
                description="View your career roadmap",
                endpoint="/v1/roadmap/current",
                method="GET",
                requires_data=False
            ))
            actions.append(NextAction(
                action="update_progress",
                title="Update Progress",
                description="Update your learning progress",
                endpoint="/v1/roadmap/progress",
                method="PUT",
                requires_data=True
            ))
        
        return actions


# ============================================================================
# Service Factory
# ============================================================================

_user_state_service = None

def get_user_state_service() -> UserStateService:
    """
    Get or create user state service instance (singleton pattern).
    
    Returns:
        UserStateService instance
    """
    global _user_state_service
    if _user_state_service is None:
        _user_state_service = UserStateService()
    return _user_state_service
