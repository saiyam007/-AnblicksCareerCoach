"""
New Roadmap Service for normalized roadmaps table.

Handles roadmap data with clean separation and versioning.
"""

from datetime import datetime
from typing import Any, Optional, Dict, List
import uuid
import json

from ...utils.database import get_dynamodb_table
from ...utils.errorHandler import get_logger
from ...models.new_schema.roadmap_model import Roadmap, RoadmapStatus

logger = get_logger(__name__)


class NewRoadmapService:
    """
    Service for managing roadmaps in the normalized roadmaps table.
    
    Handles roadmap data with clean separation:
    - Questions and answers management
    - Career path recommendations
    - Detailed roadmaps
    - Selected career path tracking
    - Versioning and history
    """
    
    def __init__(self):
        """Initialize the service with roadmaps table."""
        self.table = get_dynamodb_table('roadmaps')
        logger.info("NewRoadmapService initialized with roadmaps table")
    
    def create_roadmap(self, email: str, roadmap_data: Optional[Dict[str, Any]] = None) -> Roadmap:
        """
        Create a new roadmap for user.
        
        Args:
            email: User email address
            roadmap_data: Optional roadmap data dictionary
            
        Returns:
            Roadmap: Created roadmap object
        """
        try:
            # Default roadmap data
            default_data = {
                'email': email,
                'roadmap_id': str(uuid.uuid4()),
                'status': RoadmapStatus.QUESTIONS_GENERATED
            }
            
            # Merge with provided data
            if roadmap_data:
                default_data.update(roadmap_data)
            
            # Set timestamps
            default_data['created_at'] = datetime.utcnow().isoformat()
            default_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Create roadmap object
            roadmap = Roadmap(**default_data)
            
            # Save to DynamoDB
            self.table.put_item(Item=roadmap.to_dict())
            
            logger.info(f"Created new roadmap for user: {email}")
            return roadmap
            
        except Exception as e:
            logger.error(f"Error creating roadmap for {email}: {e}")
            raise
    
    def get_latest_roadmap(self, email: str) -> Optional[Roadmap]:
        """
        Get latest roadmap for user.
        
        Args:
            email: User email address
            
        Returns:
            Roadmap or None if not found
        """
        try:
            # Query all roadmaps and sort by created_at to get the most recent
            response = self.table.query(
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={':email': email},
                ScanIndexForward=False
            )
            
            # Sort by created_at to get the most recent
            items = response.get('Items', [])
            if items:
                # Sort by created_at descending (most recent first)
                items.sort(key=lambda x: x.get('created_at', ''), reverse=True)
                # Return the most recent item
                roadmap = Roadmap(**items[0])
                logger.info(f"Retrieved latest roadmap for: {email}")
                return roadmap
            else:
                logger.info(f"No roadmap found for: {email}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting latest roadmap for {email}: {e}")
            raise
    
    def get_roadmap_by_id(self, email: str, roadmap_id: str) -> Optional[Roadmap]:
        """
        Get specific roadmap by ID.
        
        Args:
            email: User email address
            roadmap_id: Roadmap ID
            
        Returns:
            Roadmap or None if not found
        """
        try:
            response = self.table.get_item(
                Key={
                    'email': email,
                    'roadmap_id': roadmap_id
                }
            )
            
            if 'Item' in response:
                roadmap = Roadmap.from_dict(response['Item'])
                logger.info(f"Retrieved roadmap {roadmap_id} for: {email}")
                return roadmap
            else:
                logger.info(f"Roadmap {roadmap_id} not found for: {email}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting roadmap {roadmap_id} for {email}: {e}")
            raise
    
    def get_roadmap_history(self, email: str, limit: int = 10) -> List[Roadmap]:
        """
        Get roadmap history for user.
        
        Args:
            email: User email address
            limit: Maximum number of roadmaps to return
            
        Returns:
            List of Roadmap objects
        """
        try:
            response = self.table.query(
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={':email': email},
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )
            
            roadmaps = [Roadmap.from_dict(item) for item in response.get('Items', [])]
            logger.info(f"Retrieved {len(roadmaps)} roadmaps for: {email}")
            return roadmaps
            
        except Exception as e:
            logger.error(f"Error getting roadmap history for {email}: {e}")
            raise
    
    def set_questions(self, email: str, questions: List[Dict[str, Any]], profile_snapshot: Optional[Dict[str, Any]] = None) -> Optional[Roadmap]:
        """
        Set generated questions for roadmap.
        
        Args:
            email: User email address
            questions: List of generated questions
            profile_snapshot: Profile data used for generation
            
        Returns:
            Updated Roadmap or None if not found
        """
        try:
            # Get latest roadmap or create new one
            roadmap = self.get_latest_roadmap(email)
            if not roadmap:
                roadmap = self.create_roadmap(email)
            
            # Set questions
            roadmap.set_questions(questions, profile_snapshot)
            
            # Save to database
            self.table.put_item(Item=roadmap.to_dict())
            
            logger.info(f"Set {len(questions)} questions for roadmap: {roadmap.roadmap_id}")
            return roadmap
            
        except Exception as e:
            logger.error(f"Error setting questions for {email}: {e}")
            return None
    
    def set_answers(self, email: str, answers: List[Dict[str, Any]]) -> Optional[Roadmap]:
        """
        Set user answers for roadmap.
        
        Args:
            email: User email address
            answers: List of user answers
            
        Returns:
            Updated Roadmap or None if not found
        """
        try:
            # Get latest roadmap
            roadmap = self.get_latest_roadmap(email)
            if not roadmap:
                logger.warning(f"No roadmap found for {email}")
                return None
            
            # Set answers
            roadmap.set_answers(answers)
            
            # Save to database
            self.table.put_item(Item=roadmap.to_dict())
            
            logger.info(f"Set {len(answers)} answers for roadmap: {roadmap.roadmap_id}")
            return roadmap
            
        except Exception as e:
            logger.error(f"Error setting answers for {email}: {e}")
            return None
    
    def set_career_paths(self, email: str, career_paths: List[Dict[str, Any]]) -> Optional[Roadmap]:
        """
        Set generated career paths for roadmap.
        
        Args:
            email: User email address
            career_paths: List of generated career paths
            
        Returns:
            Updated Roadmap or None if not found
        """
        try:
            # Get latest roadmap
            roadmap = self.get_latest_roadmap(email)
            if not roadmap:
                logger.warning(f"No roadmap found for {email}")
                return None
            
            # Set career paths
            roadmap.set_career_paths(career_paths)
            
            # Save to database
            self.table.put_item(Item=roadmap.to_dict())
            
            logger.info(f"Set {len(career_paths)} career paths for roadmap: {roadmap.roadmap_id}")
            return roadmap
            
        except Exception as e:
            logger.error(f"Error setting career paths for {email}: {e}")
            return None
    
    def select_career_path(self, email: str, selected_path: Dict[str, Any]) -> Optional[Roadmap]:
        """
        Set selected career path for roadmap.
        
        Args:
            email: User email address
            selected_path: Selected career path data
            
        Returns:
            Updated Roadmap or None if not found
        """
        try:
            # Get latest roadmap
            roadmap = self.get_latest_roadmap(email)
            if not roadmap:
                logger.warning(f"No roadmap found for {email}")
                return None
            
            # Set selected career path
            roadmap.select_career_path(selected_path)
            
            # Save to database
            self.table.put_item(Item=roadmap.to_dict())
            
            logger.info(f"Selected career path for roadmap: {roadmap.roadmap_id}")
            return roadmap
            
        except Exception as e:
            logger.error(f"Error selecting career path for {email}: {e}")
            return None
    
    def set_detailed_roadmap(self, email: str, detailed_roadmap: Dict[str, Any]) -> Optional[Roadmap]:
        """
        Set detailed roadmap for roadmap.
        
        Args:
            email: User email address
            detailed_roadmap: Detailed roadmap data
            
        Returns:
            Updated Roadmap or None if not found
        """
        try:
            # Get latest roadmap
            roadmap = self.get_latest_roadmap(email)
            if not roadmap:
                logger.warning(f"No roadmap found for {email}")
                return None
            
            # Set detailed roadmap
            roadmap.set_detailed_roadmap(detailed_roadmap)
            
            # Save to database
            self.table.put_item(Item=roadmap.to_dict())
            
            # Create assessment records for all topics in the roadmap
            try:
                from .assessment_service import get_new_assessment_service
                assessment_service = get_new_assessment_service()
                assessment_records = assessment_service.create_assessments_for_roadmap(
                    email=email,
                    roadmap_id=roadmap.roadmap_id,
                    roadmap_data=detailed_roadmap
                )
                logger.info(f"Created {len(assessment_records)} assessment records for roadmap {roadmap.roadmap_id}")
            except Exception as e:
                logger.warning(f"Failed to create assessment records: {e}")
            
            logger.info(f"Set detailed roadmap for roadmap: {roadmap.roadmap_id}")
            return roadmap
            
        except Exception as e:
            logger.error(f"Error setting detailed roadmap for {email}: {e}")
            return None
    
    def get_questions(self, email: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get questions for latest roadmap.
        
        Args:
            email: User email address
            
        Returns:
            List of questions or None if not found
        """
        try:
            roadmap = self.get_latest_roadmap(email)
            if roadmap:
                return roadmap.get_questions()
            return None
            
        except Exception as e:
            logger.error(f"Error getting questions for {email}: {e}")
            return None
    
    def get_answers(self, email: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get answers for latest roadmap.
        
        Args:
            email: User email address
            
        Returns:
            List of answers or None if not found
        """
        try:
            roadmap = self.get_latest_roadmap(email)
            if roadmap:
                return roadmap.get_answers()
            return None
            
        except Exception as e:
            logger.error(f"Error getting answers for {email}: {e}")
            return None
    
    def get_career_paths(self, email: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get career paths for latest roadmap.
        
        Args:
            email: User email address
            
        Returns:
            List of career paths or None if not found
        """
        try:
            roadmap = self.get_latest_roadmap(email)
            if roadmap:
                return roadmap.get_career_paths()
            return None
            
        except Exception as e:
            logger.error(f"Error getting career paths for {email}: {e}")
            return None
    
    def get_selected_career_path(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get selected career path for latest roadmap.
        
        Args:
            email: User email address
            
        Returns:
            Selected career path or None if not found
        """
        try:
            roadmap = self.get_latest_roadmap(email)
            if roadmap:
                return roadmap.get_selected_career_path()
            return None
            
        except Exception as e:
            logger.error(f"Error getting selected career path for {email}: {e}")
            return None
    
    def get_detailed_roadmap(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed roadmap for latest roadmap.
        
        Args:
            email: User email address
            
        Returns:
            Detailed roadmap or None if not found
        """
        try:
            roadmap = self.get_latest_roadmap(email)
            if roadmap:
                return roadmap.get_detailed_roadmap()
            return None
            
        except Exception as e:
            logger.error(f"Error getting detailed roadmap for {email}: {e}")
            return None
    
    def is_questions_ready(self, email: str) -> bool:
        """
        Check if questions are ready for latest roadmap.
        
        Args:
            email: User email address
            
        Returns:
            True if questions are ready
        """
        try:
            roadmap = self.get_latest_roadmap(email)
            if roadmap:
                return roadmap.is_questions_ready()
            return False
            
        except Exception as e:
            logger.error(f"Error checking questions readiness for {email}: {e}")
            return False
    
    def is_answers_ready(self, email: str) -> bool:
        """
        Check if answers are ready for latest roadmap.
        
        Args:
            email: User email address
            
        Returns:
            True if answers are ready
        """
        try:
            roadmap = self.get_latest_roadmap(email)
            if roadmap:
                return roadmap.is_answers_ready()
            return False
            
        except Exception as e:
            logger.error(f"Error checking answers readiness for {email}: {e}")
            return False
    
    def is_career_paths_ready(self, email: str) -> bool:
        """
        Check if career paths are ready for latest roadmap.
        
        Args:
            email: User email address
            
        Returns:
            True if career paths are ready
        """
        try:
            roadmap = self.get_latest_roadmap(email)
            if roadmap:
                return roadmap.is_career_paths_ready()
            return False
            
        except Exception as e:
            logger.error(f"Error checking career paths readiness for {email}: {e}")
            return False
    
    def is_detailed_roadmap_ready(self, email: str) -> bool:
        """
        Check if detailed roadmap is ready for latest roadmap.
        
        Args:
            email: User email address
            
        Returns:
            True if detailed roadmap is ready
        """
        try:
            roadmap = self.get_latest_roadmap(email)
            if roadmap:
                return roadmap.is_detailed_roadmap_ready()
            return False
            
        except Exception as e:
            logger.error(f"Error checking detailed roadmap readiness for {email}: {e}")
            return False
    
    def get_roadmap_summary(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get roadmap summary for API responses.
        
        Args:
            email: User email address
            
        Returns:
            Roadmap summary dictionary or None
        """
        try:
            roadmap = self.get_latest_roadmap(email)
            if roadmap:
                return roadmap.get_roadmap_summary()
            return None
            
        except Exception as e:
            logger.error(f"Error getting roadmap summary for {email}: {e}")
            return None
    
    def roadmap_exists(self, email: str) -> bool:
        """
        Check if user has any roadmap.
        
        Args:
            email: User email address
            
        Returns:
            True if roadmap exists, False otherwise
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
            logger.error(f"Error checking if roadmap exists for {email}: {e}")
            return False
    
    def delete_roadmap(self, email: str, roadmap_id: str) -> bool:
        """
        Delete specific roadmap.
        
        Args:
            email: User email address
            roadmap_id: Roadmap ID to delete
            
        Returns:
            True if successful
        """
        try:
            self.table.delete_item(
                Key={
                    'email': email,
                    'roadmap_id': roadmap_id
                }
            )
            
            logger.info(f"Deleted roadmap {roadmap_id} for: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting roadmap {roadmap_id} for {email}: {e}")
            return False


# Dependency injection
_new_roadmap_service: Optional[NewRoadmapService] = None


def get_new_roadmap_service() -> NewRoadmapService:
    """
    Get or create NewRoadmapService instance (singleton pattern).
    
    Returns:
        NewRoadmapService instance
    """
    global _new_roadmap_service
    if _new_roadmap_service is None:
        _new_roadmap_service = NewRoadmapService()
    return _new_roadmap_service
