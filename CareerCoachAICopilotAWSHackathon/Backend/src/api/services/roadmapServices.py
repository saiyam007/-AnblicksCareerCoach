"""
Roadmap Service for UserCareerRoadmaps table management.

Business logic for roadmap lifecycle:
- Question generation and caching
- Roadmap generation and storage
- Profile update handling (roadmap deletion)
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError

from ..utils.database import get_dynamodb_table
from ..utils.errorHandler import get_logger

logger = get_logger(__name__)


class RoadmapService:
    """Service class for UserCareerRoadmaps table operations."""
    
    def __init__(self):
        """Initialize roadmap service with DynamoDB table."""
        self.table = get_dynamodb_table('UserCareerRoadmaps')
        logger.info(" RoadmapService initialized with UserCareerRoadmaps table")
    
    def get_latest_questions(self, email: str) -> Optional[Dict]:
        """
        Get latest roadmap with QUESTIONS_GENERATED status.
        
        Args:
            email: User email
            
        Returns:
            Roadmap data if found, None if not found
        """
        try:
            response = self.table.query(
                KeyConditionExpression="email = :email",
                FilterExpression="#status = :status",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":email": email,
                    ":status": "QUESTIONS_GENERATED"
                },
                ScanIndexForward=False,  # Descending order (latest first)
                Limit=1
            )
            
            items = response.get('Items', [])
            if items:
                logger.info(f"Found existing questions for user: {email}")
                item = items[0]
                # Parse JSON strings back to objects
                if 'questions' in item and isinstance(item['questions'], str):
                    item['questions'] = json.loads(item['questions'])
                if 'profile' in item and isinstance(item['profile'], str):
                    item['profile'] = json.loads(item['profile'])
                return item
            
            logger.info(f"No existing questions found for user: {email}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest questions for {email}: {e}")
            return None
    
    def save_questions_only(self, email: str, questions: Dict, profile: Dict) -> Dict:
        """
        Save questions to new roadmap record.
        
        Args:
            email: User email
            questions: Generated questions data
            profile: User profile data
            
        Returns:
            Created roadmap data with roadmapId
        """
        try:
            roadmap_id = str(uuid.uuid4())
            current_time = datetime.utcnow().isoformat()
            
            roadmap_data = {
                "email": email,
                "roadmapId": roadmap_id,
                "status": "QUESTIONS_GENERATED",
                "questions": json.dumps(questions),  # Store as JSON string
                "profile": json.dumps(profile),      # Store as JSON string
                "createdAt": current_time,
                "updatedAt": current_time
            }
            
            self.table.put_item(Item=roadmap_data)
            
            logger.info(f"Saved questions for user {email} with roadmapId: {roadmap_id}")
            
            return {
                "roadmapId": roadmap_id,
                "status": "QUESTIONS_GENERATED",
                "questions": questions,
                "createdAt": current_time
            }
            
        except Exception as e:
            logger.error(f"Error saving questions for {email}: {e}")
            raise RuntimeError(f"Failed to save questions: {e}")
    
    def update_with_roadmap(self, email: str, roadmap_id: str, answers: List[Dict], roadmap: Dict) -> Dict:
        """
        Update existing roadmap with answers and generated roadmap.
        
        Args:
            email: User email
            roadmap_id: Roadmap ID
            answers: User answers to questions
            roadmap: Generated career roadmap
            
        Returns:
            Updated roadmap data
        """
        try:
            current_time = datetime.utcnow().isoformat()
            
            # Update the existing item
            update_expression = "SET #status = :status, answers = :answers, roadmap = :roadmap, updatedAt = :updatedAt"
            expression_attribute_names = {
                "#status": "status"
            }
            expression_attribute_values = {
                ":status": "ROADMAP_COMPLETED",
                ":answers": json.dumps(answers),  # Store as JSON string
                ":roadmap": json.dumps(roadmap),  # Store as JSON string
                ":updatedAt": current_time
            }
            
            self.table.update_item(
                Key={
                    "email": email,
                    "roadmapId": roadmap_id
                },
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW"
            )
            
            logger.info(f"Updated roadmap {roadmap_id} for user {email} with answers and roadmap")
            
            return {
                "roadmapId": roadmap_id,
                "status": "ROADMAP_COMPLETED",
                "answers": answers,
                "roadmap": roadmap,
                "updatedAt": current_time
            }
            
        except Exception as e:
            logger.error(f"Error updating roadmap {roadmap_id} for {email}: {e}")
            raise RuntimeError(f"Failed to update roadmap: {e}")
    
    def delete_user_roadmaps(self, email: str) -> Dict:
        """
        Delete all roadmaps for a user when their profile changes.
        
        Args:
            email: User email
            
        Returns:
            Deletion result with count
        """
        try:
            # Get all roadmaps for the user
            response = self.table.query(
                KeyConditionExpression="email = :email",
                ExpressionAttributeValues={":email": email}
            )
            
            items = response.get('Items', [])
            
            if not items:
                logger.info(f"No roadmaps found for user: {email}")
                return {"deleted_count": 0}
            
            # Delete each roadmap
            deleted_count = 0
            for item in items:
                try:
                    self.table.delete_item(
                        Key={
                            "email": email,
                            "roadmapId": item["roadmapId"]
                        }
                    )
                    deleted_count += 1
                    logger.info(f"Deleted roadmap {item['roadmapId']} for user {email}")
                except Exception as e:
                    logger.error(f"Failed to delete roadmap {item['roadmapId']}: {e}")
            
            logger.info(f"Deleted {deleted_count} roadmaps for user: {email}")
            return {"deleted_count": deleted_count}
            
        except Exception as e:
            logger.error(f"Error deleting roadmaps for user {email}: {e}")
            raise RuntimeError(f"Failed to delete roadmaps: {e}")
    
    def get_latest_roadmap(self, email: str) -> Optional[Dict]:
        """
        Get most recent roadmap for user (any status).
        
        Args:
            email: User email
            
        Returns:
            Latest roadmap data if found, None if not found
        """
        try:
            response = self.table.query(
                KeyConditionExpression="email = :email",
                ExpressionAttributeValues={":email": email},
                ScanIndexForward=False,  # Descending order (latest first)
                Limit=1
            )
            
            items = response.get('Items', [])
            if items:
                logger.info(f"Found latest roadmap for user: {email}")
                item = items[0]
                # Parse JSON strings back to objects
                if 'questions' in item and isinstance(item['questions'], str):
                    item['questions'] = json.loads(item['questions'])
                if 'answers' in item and isinstance(item['answers'], str):
                    item['answers'] = json.loads(item['answers'])
                if 'roadmap' in item and isinstance(item['roadmap'], str):
                    item['roadmap'] = json.loads(item['roadmap'])
                if 'selectedCareerPath' in item and isinstance(item['selectedCareerPath'], str):
                    item['selectedCareerPath'] = json.loads(item['selectedCareerPath'])
                if 'detailedRoadmap' in item and isinstance(item['detailedRoadmap'], str):
                    item['detailedRoadmap'] = json.loads(item['detailedRoadmap'])
                if 'profile' in item and isinstance(item['profile'], str):
                    item['profile'] = json.loads(item['profile'])
                return item
            
            logger.info(f"No roadmaps found for user: {email}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest roadmap for {email}: {e}")
            return None
    
    def get_user_roadmaps(self, email: str) -> List[Dict]:
        """
        Get all roadmaps for a user.
        
        Args:
            email: User email
            
        Returns:
            List of all roadmaps for the user
        """
        try:
            response = self.table.query(
                KeyConditionExpression="email = :email",
                ExpressionAttributeValues={":email": email},
                ScanIndexForward=False  # Descending order (latest first)
            )
            
            items = response.get('Items', [])
            logger.info(f"Retrieved {len(items)} roadmaps for user: {email}")
            
            # Parse JSON strings back to objects for all items
            parsed_items = []
            for item in items:
                # Parse JSON strings back to objects
                if 'questions' in item and isinstance(item['questions'], str):
                    item['questions'] = json.loads(item['questions'])
                if 'answers' in item and isinstance(item['answers'], str):
                    item['answers'] = json.loads(item['answers'])
                if 'roadmap' in item and isinstance(item['roadmap'], str):
                    item['roadmap'] = json.loads(item['roadmap'])
                if 'selectedCareerPath' in item and isinstance(item['selectedCareerPath'], str):
                    item['selectedCareerPath'] = json.loads(item['selectedCareerPath'])
                if 'detailedRoadmap' in item and isinstance(item['detailedRoadmap'], str):
                    item['detailedRoadmap'] = json.loads(item['detailedRoadmap'])
                if 'profile' in item and isinstance(item['profile'], str):
                    item['profile'] = json.loads(item['profile'])
                parsed_items.append(item)
            
            return parsed_items
            
        except Exception as e:
            logger.error(f"Error getting roadmaps for {email}: {e}")
            return []

    def update_with_detailed_roadmap(self, email: str, roadmap_id: str, detailed_roadmap: Dict, selected_career_path: Dict = None) -> Dict:
        """
        Update an existing roadmap record with detailed roadmap data and selected career path.
        
        Args:
            email: User's email address
            roadmap_id: Roadmap ID to update
            detailed_roadmap: Complete detailed roadmap structure
            selected_career_path: User's selected career path data
            
        Returns:
            Dict: Updated roadmap data
            
        Raises:
            Exception: If update fails
        """
        try:
            # Prepare update expression and values
            update_expression = 'SET detailedRoadmap = :detailed_roadmap, #status = :status, updatedAt = :updated_at'
            expression_attribute_values = {
                ':detailed_roadmap': json.dumps(detailed_roadmap),
                ':status': 'DETAILED_ROADMAP_COMPLETED',
                ':updated_at': datetime.utcnow().isoformat()
            }
            
            # Add selected career path if provided
            if selected_career_path:
                update_expression += ', selectedCareerPath = :selected_career_path'
                expression_attribute_values[':selected_career_path'] = json.dumps(selected_career_path)
            
            # Update the roadmap record with detailed roadmap and selected career path
            response = self.table.update_item(
                Key={
                    'email': email,
                    'roadmapId': roadmap_id
                },
                UpdateExpression=update_expression,
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            
            updated_item = response['Attributes']
            
            # Parse JSON strings back to objects for response
            if 'detailedRoadmap' in updated_item and isinstance(updated_item['detailedRoadmap'], str):
                updated_item['detailedRoadmap'] = json.loads(updated_item['detailedRoadmap'])
            if 'selectedCareerPath' in updated_item and isinstance(updated_item['selectedCareerPath'], str):
                updated_item['selectedCareerPath'] = json.loads(updated_item['selectedCareerPath'])
            if 'questions' in updated_item and isinstance(updated_item['questions'], str):
                updated_item['questions'] = json.loads(updated_item['questions'])
            if 'answers' in updated_item and isinstance(updated_item['answers'], str):
                updated_item['answers'] = json.loads(updated_item['answers'])
            if 'roadmap' in updated_item and isinstance(updated_item['roadmap'], str):
                updated_item['roadmap'] = json.loads(updated_item['roadmap'])
            if 'profile' in updated_item and isinstance(updated_item['profile'], str):
                updated_item['profile'] = json.loads(updated_item['profile'])
            
            logger.info(f"Updated roadmap {roadmap_id} with detailed roadmap for {email}")
            return updated_item
            
        except Exception as e:
            logger.error(f"Error updating roadmap with detailed roadmap: {e}")
            raise


# ============================================================================
# Dependency Injection
# ============================================================================

# Global service instance
_roadmap_service = None

def get_roadmap_service() -> RoadmapService:
    """
    Get or create roadmap service instance (singleton pattern).
    
    Returns:
        RoadmapService instance
    """
    global _roadmap_service
    if _roadmap_service is None:
        _roadmap_service = RoadmapService()
    return _roadmap_service
