"""
User Journey Service for normalized user_journey table.

Handles journey state management with detailed tracking.
"""

from datetime import datetime
from typing import Any, Optional, Dict, List
import uuid
from decimal import Decimal

from ...utils.database import get_dynamodb_table
from ...utils.errorHandler import get_logger
from ...models.new_schema.journey_model import UserJourney, JourneyStatus
from ...models.enums import JourneyStage

logger = get_logger(__name__)


class UserJourneyService:
    """
    Service for managing user journeys in the normalized user_journey table.
    
    Handles journey state management:
    - Journey creation and stage transitions
    - Progress tracking and analytics
    - Journey history and status management
    - Performance metrics and engagement tracking
    """
    
    def __init__(self):
        """Initialize the service with user_journey table."""
        self.table = get_dynamodb_table('user_journey')
        logger.info("UserJourneyService initialized with user_journey table")
    
    def create_journey(self, email: str, journey_data: Optional[Dict[str, Any]] = None) -> UserJourney:
        """
        Create a new user journey.
        
        Args:
            email: User email address
            journey_data: Optional journey data dictionary
            
        Returns:
            UserJourney: Created journey object
        """
        try:
            # Default journey data
            default_data = {
                'email': email,
                'journey_id': str(uuid.uuid4()),
                'is_active': 'true',
                'current_stage': JourneyStage.AUTHENTICATED.value,
                'status': JourneyStatus.ACTIVE.value,
                'progress_percentage': Decimal('0.0'),
                'total_steps': 7,
                'completed_steps': 0,
                'current_step': 1,
                'journey_type': 'standard'
            }
            
            # Merge with provided data
            if journey_data:
                default_data.update(journey_data)
            
            # Set timestamps
            default_data['created_at'] = datetime.utcnow().isoformat()
            default_data['updated_at'] = datetime.utcnow().isoformat()
            default_data['started_at'] = datetime.utcnow().isoformat()
            default_data['last_activity_at'] = datetime.utcnow().isoformat()
            
            # Create journey object
            journey = UserJourney(**default_data)
            
            # Save to DynamoDB
            self.table.put_item(Item=journey.to_dict())
            
            logger.info(f"Created new journey for user: {email}")
            return journey
            
        except Exception as e:
            logger.error(f"Error creating journey for {email}: {e}")
            raise
    
    def get_active_journey(self, email: str) -> Optional[UserJourney]:
        """
        Get active journey for user.
        
        Args:
            email: User email address
            
        Returns:
            UserJourney or None if not found
        """
        try:
            response = self.table.query(
                KeyConditionExpression='email = :email',
                FilterExpression='is_active = :active',
                ExpressionAttributeValues={
                    ':email': email,
                    ':active': 'true'
                },
                ScanIndexForward=False,  # Most recent first
                Limit=1
            )
            
            if response['Items']:
                journey = UserJourney.from_dict(response['Items'][0])
                logger.info(f"Retrieved active journey for: {email}")
                return journey
            else:
                logger.info(f"No active journey found for: {email}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting active journey for {email}: {e}")
            raise
    
    def get_journey_by_id(self, email: str, journey_id: str) -> Optional[UserJourney]:
        """
        Get specific journey by ID.
        
        Args:
            email: User email address
            journey_id: Journey ID
            
        Returns:
            UserJourney or None if not found
        """
        try:
            response = self.table.get_item(
                Key={
                    'email': email,
                    'journey_id': journey_id
                }
            )
            
            if 'Item' in response:
                journey = UserJourney.from_dict(response['Item'])
                logger.info(f"Retrieved journey {journey_id} for: {email}")
                return journey
            else:
                logger.info(f"Journey {journey_id} not found for: {email}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting journey {journey_id} for {email}: {e}")
            raise
    
    def get_journey_history(self, email: str, limit: int = 10) -> List[UserJourney]:
        """
        Get journey history for user.
        
        Args:
            email: User email address
            limit: Maximum number of journeys to return
            
        Returns:
            List of UserJourney objects
        """
        try:
            response = self.table.query(
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={':email': email},
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )
            
            journeys = [UserJourney.from_dict(item) for item in response.get('Items', [])]
            logger.info(f"Retrieved {len(journeys)} journeys for: {email}")
            return journeys
            
        except Exception as e:
            logger.error(f"Error getting journey history for {email}: {e}")
            raise
    
    def transition_to_stage(self, email: str, new_stage: str, transition_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Transition user journey to a new stage.
        
        Args:
            email: User email address
            new_stage: New journey stage
            transition_data: Optional transition data
            
        Returns:
            True if successful
        """
        try:
            # Get active journey
            journey = self.get_active_journey(email)
            if not journey:
                logger.warning(f"No active journey found for {email}")
                return False
            
            # Record transition
            journey.transition_to_stage(new_stage, transition_data)
            
            # Update in database
            self.table.put_item(Item=journey.to_dict())
            
            logger.info(f"Transitioned {email} from {journey.stage_transitions[-1]['from_stage']} to {new_stage}")
            return True
            
        except Exception as e:
            logger.error(f"Error transitioning journey for {email}: {e}")
            return False
    
    def update_journey(self, email: str, updates: Dict[str, Any]) -> Optional[UserJourney]:
        """
        Update journey data.
        
        Args:
            email: User email address
            updates: Dictionary of fields to update
            
        Returns:
            Updated UserJourney or None if not found
        """
        try:
            # Get active journey
            journey = self.get_active_journey(email)
            if not journey:
                logger.warning(f"No active journey found for {email}")
                return None
            
            # Update fields
            for key, value in updates.items():
                if hasattr(journey, key):
                    setattr(journey, key, value)
            
            # Update timestamp
            journey.updated_at = datetime.utcnow().isoformat()
            journey.last_activity_at = datetime.utcnow().isoformat()
            
            # Save to database
            self.table.put_item(Item=journey.to_dict())
            
            logger.info(f"Updated journey for: {email}")
            return journey
            
        except Exception as e:
            logger.error(f"Error updating journey for {email}: {e}")
            return None
    
    def set_roadmap_id(self, email: str, roadmap_id: str) -> bool:
        """
        Set roadmap ID for active journey.
        
        Args:
            email: User email address
            roadmap_id: Roadmap ID to link
            
        Returns:
            True if successful
        """
        try:
            journey = self.get_active_journey(email)
            if not journey:
                logger.warning(f"No active journey found for {email}")
                return False
            
            journey.roadmap_id = roadmap_id
            journey.updated_at = datetime.utcnow().isoformat()
            journey.last_activity_at = datetime.utcnow().isoformat()
            
            # Save to database
            self.table.put_item(Item=journey.to_dict())
            
            logger.info(f"Set roadmap ID {roadmap_id} for journey: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting roadmap ID for {email}: {e}")
            return False
    
    def add_assessment(self, email: str, assessment_id: str) -> bool:
        """
        Add completed assessment to active journey.
        
        Args:
            email: User email address
            assessment_id: Assessment ID to add
            
        Returns:
            True if successful
        """
        try:
            journey = self.get_active_journey(email)
            if not journey:
                logger.warning(f"No active journey found for {email}")
                return False
            
            journey.add_assessment(assessment_id)
            
            # Save to database
            self.table.put_item(Item=journey.to_dict())
            
            logger.info(f"Added assessment {assessment_id} to journey: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding assessment for {email}: {e}")
            return False
    
    def update_skill_progress(self, email: str, skill: str, progress: float) -> bool:
        """
        Update skill development progress.
        
        Args:
            email: User email address
            skill: Skill name
            progress: Progress percentage (0.0 to 1.0)
            
        Returns:
            True if successful
        """
        try:
            journey = self.get_active_journey(email)
            if not journey:
                logger.warning(f"No active journey found for {email}")
                return False
            
            journey.update_skill_progress(skill, progress)
            
            # Save to database
            self.table.put_item(Item=journey.to_dict())
            
            logger.info(f"Updated skill progress for {skill}: {progress:.1%}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating skill progress for {email}: {e}")
            return False
    
    def pause_journey(self, email: str, reason: Optional[str] = None) -> bool:
        """
        Pause active journey.
        
        Args:
            email: User email address
            reason: Optional pause reason
            
        Returns:
            True if successful
        """
        try:
            journey = self.get_active_journey(email)
            if not journey:
                logger.warning(f"No active journey found for {email}")
                return False
            
            journey.pause_journey(reason)
            
            # Save to database
            self.table.put_item(Item=journey.to_dict())
            
            logger.info(f"Paused journey for: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error pausing journey for {email}: {e}")
            return False
    
    def resume_journey(self, email: str) -> bool:
        """
        Resume paused journey.
        
        Args:
            email: User email address
            
        Returns:
            True if successful
        """
        try:
            journey = self.get_active_journey(email)
            if not journey:
                logger.warning(f"No active journey found for {email}")
                return False
            
            journey.resume_journey()
            
            # Save to database
            self.table.put_item(Item=journey.to_dict())
            
            logger.info(f"Resumed journey for: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error resuming journey for {email}: {e}")
            return False
    
    def complete_journey(self, email: str) -> bool:
        """
        Mark journey as completed.
        
        Args:
            email: User email address
            
        Returns:
            True if successful
        """
        try:
            journey = self.get_active_journey(email)
            if not journey:
                logger.warning(f"No active journey found for {email}")
                return False
            
            journey.complete_journey()
            
            # Save to database
            self.table.put_item(Item=journey.to_dict())
            
            logger.info(f"Completed journey for: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error completing journey for {email}: {e}")
            return False
    
    def get_current_stage(self, email: str) -> Optional[str]:
        """
        Get current journey stage for user.
        
        Args:
            email: User email address
            
        Returns:
            Current stage string or None
        """
        try:
            journey = self.get_active_journey(email)
            if journey:
                return journey.current_stage
            return None
            
        except Exception as e:
            logger.error(f"Error getting current stage for {email}: {e}")
            return None
    
    def get_journey_progress(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get journey progress information.
        
        Args:
            email: User email address
            
        Returns:
            Progress information dictionary or None
        """
        try:
            journey = self.get_active_journey(email)
            if not journey:
                return None
            
            return journey.get_stage_info()
            
        except Exception as e:
            logger.error(f"Error getting journey progress for {email}: {e}")
            return None
    
    def get_journey_summary(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get journey summary for API responses.
        
        Args:
            email: User email address
            
        Returns:
            Journey summary dictionary or None
        """
        try:
            journey = self.get_active_journey(email)
            if not journey:
                return None
            
            return journey.get_journey_summary()
            
        except Exception as e:
            logger.error(f"Error getting journey summary for {email}: {e}")
            return None
    
    def journey_exists(self, email: str) -> bool:
        """
        Check if user has any journey.
        
        Args:
            email: User email address
            
        Returns:
            True if journey exists, False otherwise
        """
        try:
            response = self.table.query(
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={':email': email},
                Limit=1,
                ProjectionExpression='email'
            )
            
            return len(response.get('Items', [])) > 0
            
        except Exception as e:
            logger.error(f"Error checking if journey exists for {email}: {e}")
            return False


# Dependency injection
_user_journey_service: Optional[UserJourneyService] = None


def get_user_journey_service() -> UserJourneyService:
    """
    Get or create UserJourneyService instance (singleton pattern).
    
    Returns:
        UserJourneyService instance
    """
    global _user_journey_service
    if _user_journey_service is None:
        _user_journey_service = UserJourneyService()
    return _user_journey_service
