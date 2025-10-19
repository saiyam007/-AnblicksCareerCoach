"""
New Roadmap Service using the normalized schema.

This service handles roadmap and assessment operations using the new
normalized database schema while maintaining backward compatibility.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from ..utils.errorHandler import get_logger
from ..utils.database import get_dynamodb_table

# Import new schema services
from .new_schema.roadmap_service import get_new_roadmap_service
from .new_schema.assessment_service import get_new_assessment_service
from .new_schema.journey_service import get_user_journey_service

logger = get_logger(__name__)


class NewRoadmapService:
    """Service class for roadmap operations using new schema."""
    
    def __init__(self):
        """Initialize with new schema services."""
        self.roadmap_service = get_new_roadmap_service()
        self.assessment_service = get_new_assessment_service()
        self.journey_service = get_user_journey_service()
        self.table = get_dynamodb_table('roadmaps')
    
    def save_questions_only(self, email: str, questions: Dict, profile: Dict) -> Dict:
        """
        Save questions only (without answers) using new schema.
        
        Args:
            email: User email address
            questions: Generated questions
            profile: User profile data
            
        Returns:
            Dict: Saved roadmap data with questions
        """
        try:
            # Debug: Log the data being passed
            logger.info(f"Email type: {type(email)}, value: {email}")
            logger.info(f"Questions type: {type(questions)}, keys: {questions.keys() if isinstance(questions, dict) else 'not a dict'}")
            
            # Serialize questions to JSON string for DynamoDB
            questions_json = json.dumps(questions) if not isinstance(questions, str) else questions
            
            # Create roadmap in new schema
            roadmap_data = {
                'email': email,
                'status': 'QUESTIONS_GENERATED',
                'questions': questions_json,
                'questions_generated_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Roadmap data keys: {roadmap_data.keys()}")
            # Bypass roadmap service and save directly to DynamoDB
            roadmap_id = str(uuid.uuid4())
            roadmap_data['roadmap_id'] = roadmap_id
            roadmap_data['created_at'] = datetime.utcnow().isoformat()
            roadmap_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Save directly to DynamoDB
            self.table.put_item(Item=roadmap_data)
            
            logger.info(f"Saved questions for user: {email} with roadmap ID: {roadmap_id}")
            
            return {
                "roadmapId": roadmap_id,
                "status": "QUESTIONS_GENERATED",
                "questions": questions,
                "profile": profile,
                "createdAt": roadmap_data['created_at']
            }
            
        except Exception as e:
            logger.error(f"Error saving questions for {email}: {e}")
            raise RuntimeError(f"Failed to save questions: {e}")
    
    def update_with_roadmap(self, email: str, roadmap_id: str, answers: List[Dict], roadmap: Dict) -> Dict:
        """
        Update roadmap with answers and generated roadmap using new schema.
        
        Args:
            email: User email address
            roadmap_id: Roadmap ID
            answers: User answers to questions
            roadmap: Generated career roadmap
            
        Returns:
            Dict: Updated roadmap data
        """
        try:
            # Update roadmap in new schema
            update_data = {
                'status': 'CAREER_PATHS_GENERATED',  # ✅ FIXED: Should be CAREER_PATHS_GENERATED, not ROADMAP_COMPLETED
                'answers': answers,
                'roadmap': roadmap,
                'metadata': {
                    'updated_for': 'roadmap_generation',
                    'source': 'ai_service'
                }
            }
            
            # Update directly in DynamoDB
            self.table.update_item(
                Key={
                    'email': email,
                    'roadmap_id': roadmap_id
                },
                UpdateExpression='SET #status = :status, answers = :answers, career_paths = :career_paths, updated_at = :updated_at',
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':status': 'CAREER_PATHS_GENERATED',  # ✅ FIXED: Should be CAREER_PATHS_GENERATED
                    ':answers': json.dumps(answers),
                    ':career_paths': json.dumps(roadmap),
                    ':updated_at': datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Updated roadmap {roadmap_id} for user {email} with answers and roadmap")
            
            return {
                "roadmapId": roadmap_id,
                "status": "CAREER_PATHS_GENERATED",  # ✅ FIXED: Should be CAREER_PATHS_GENERATED
                "answers": answers,
                "roadmap": roadmap,
                "updatedAt": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error updating roadmap {roadmap_id} for {email}: {e}")
            raise RuntimeError(f"Failed to update roadmap: {e}")
    
    def update_with_detailed_roadmap(self, email: str, roadmap_id: str, detailed_roadmap: Dict, selected_career_path: Dict = None) -> Dict:
        """
        Update roadmap with detailed roadmap data using new schema.
        
        Args:
            email: User email address
            roadmap_id: Roadmap ID
            detailed_roadmap: Complete detailed roadmap structure
            selected_career_path: User's selected career path data
            
        Returns:
            Dict: Updated roadmap data
        """
        try:
            # First select the career path if provided
            if selected_career_path:
                self.roadmap_service.select_career_path(email, selected_career_path)
            
            # Then set the detailed roadmap
            updated_roadmap = self.roadmap_service.set_detailed_roadmap(email, detailed_roadmap)
            
            if not updated_roadmap:
                raise RuntimeError("Failed to update roadmap with detailed roadmap")
            
            logger.info(f"Updated roadmap {roadmap_id} with detailed roadmap for {email}")
            
            return {
                "roadmapId": roadmap_id,
                "status": "ROADMAP_COMPLETED",  # ✅ FIXED: Should be ROADMAP_COMPLETED
                "detailedRoadmap": detailed_roadmap,
                "selectedCareerPath": selected_career_path,
                "updatedAt": updated_roadmap.updated_at
            }
            
        except Exception as e:
            logger.error(f"Error updating roadmap with detailed roadmap: {e}")
            raise
    
    def get_latest_roadmap(self, email: str) -> Optional[Dict]:
        """
        Get latest roadmap for user using new schema.
        
        Args:
            email: User email address
            
        Returns:
            Dict: Latest roadmap data or None
        """
        try:
            roadmap = self.roadmap_service.get_latest_roadmap(email)
            if not roadmap:
                return None
            
            # Convert to legacy format for backward compatibility
            legacy_data = {
                "roadmapId": roadmap.roadmap_id,
                "status": roadmap.status,
                "createdAt": roadmap.created_at,
                "updatedAt": roadmap.updated_at
            }
            
            # Add optional fields if they exist (use getter methods for proper deserialization)
            if hasattr(roadmap, 'questions') and roadmap.questions:
                legacy_data["questions"] = roadmap.get_questions()
            
            if hasattr(roadmap, 'answers') and roadmap.answers:
                legacy_data["answers"] = roadmap.get_answers()
            
            if hasattr(roadmap, 'roadmap') and roadmap.roadmap:
                legacy_data["roadmap"] = roadmap.get_career_paths()
            
            if hasattr(roadmap, 'detailed_roadmap') and roadmap.detailed_roadmap:
                legacy_data["detailedRoadmap"] = roadmap.get_detailed_roadmap()
            
            if hasattr(roadmap, 'selected_career_path') and roadmap.selected_career_path:
                legacy_data["selectedCareerPath"] = roadmap.get_selected_career_path()
            
            if hasattr(roadmap, 'profile') and roadmap.profile:
                legacy_data["profile"] = roadmap.get_profile_snapshot()
            
            logger.info(f"Retrieved latest roadmap for user: {email}")
            return legacy_data
            
        except Exception as e:
            logger.error(f"Error getting latest roadmap for {email}: {e}")
            return None
    
    def get_user_roadmaps(self, email: str, limit: int = 10) -> List[Dict]:
        """
        Get all roadmaps for user using new schema.
        
        Args:
            email: User email address
            limit: Maximum number of roadmaps to return
            
        Returns:
            List[Dict]: List of roadmap data
        """
        try:
            roadmaps = self.roadmap_service.get_roadmaps_by_user(email, limit=limit)
            
            legacy_roadmaps = []
            for roadmap in roadmaps:
                legacy_data = {
                    "roadmapId": roadmap.roadmap_id,
                    "status": roadmap.status,
                    "roadmapType": roadmap.roadmap_type,
                    "createdAt": roadmap.created_at,
                    "updatedAt": roadmap.updated_at
                }
                
                # Add optional fields if they exist (use getter methods for proper deserialization)
                if hasattr(roadmap, 'questions') and roadmap.questions:
                    legacy_data["questions"] = roadmap.get_questions()
                
                if hasattr(roadmap, 'answers') and roadmap.answers:
                    legacy_data["answers"] = roadmap.get_answers()
                
                if hasattr(roadmap, 'roadmap') and roadmap.roadmap:
                    legacy_data["roadmap"] = roadmap.get_career_paths()
                
                if hasattr(roadmap, 'detailed_roadmap') and roadmap.detailed_roadmap:
                    legacy_data["detailedRoadmap"] = roadmap.get_detailed_roadmap()
                
                if hasattr(roadmap, 'selected_career_path') and roadmap.selected_career_path:
                    legacy_data["selectedCareerPath"] = roadmap.get_selected_career_path()
                
                legacy_roadmaps.append(legacy_data)
            
            logger.info(f"Retrieved {len(legacy_roadmaps)} roadmaps for user: {email}")
            return legacy_roadmaps
            
        except Exception as e:
            logger.error(f"Error getting roadmaps for {email}: {e}")
            return []
    
    def delete_user_roadmaps(self, email: str) -> Dict:
        """
        Delete all roadmaps for user using new schema.
        
        Args:
            email: User email address
            
        Returns:
            Dict: Deletion result
        """
        try:
            deleted_count = self.roadmap_service.delete_user_roadmaps(email)
            
            logger.info(f"Deleted {deleted_count} roadmaps for user: {email}")
            
            return {
                "success": True,
                "message": f"Deleted {deleted_count} roadmaps",
                "deletedCount": deleted_count
            }
            
        except Exception as e:
            logger.error(f"Error deleting roadmaps for {email}: {e}")
            return {
                "success": False,
                "message": f"Failed to delete roadmaps: {str(e)}",
                "deletedCount": 0
            }
    
    def create_assessment(self, email: str, assessment_data: Dict) -> Dict:
        """
        Create assessment using new schema.
        
        Args:
            email: User email address
            assessment_data: Assessment data
            
        Returns:
            Dict: Created assessment data
        """
        try:
            assessment_data['email'] = email
            assessment = self.assessment_service.create_assessment(assessment_data)
            
            logger.info(f"Created assessment {assessment.assessment_id} for user: {email}")
            
            return {
                "assessmentId": assessment.assessment_id,
                "status": assessment.status,
                "skill": assessment.skill,
                "totalQuestions": assessment.total_questions,
                "createdAt": assessment.created_at
            }
            
        except Exception as e:
            logger.error(f"Error creating assessment for {email}: {e}")
            raise RuntimeError(f"Failed to create assessment: {e}")
    
    def update_assessment_with_answers(self, email: str, assessment_id: str, answers: List[Dict]) -> Dict:
        """
        Update assessment with user answers using new schema.
        
        Args:
            email: User email address
            assessment_id: Assessment ID
            answers: User answers
            
        Returns:
            Dict: Updated assessment data
        """
        try:
            # Update assessment with answers
            update_data = {
                'user_answers': answers,
                'status': 'COMPLETED'
            }
            
            updated_assessment = self.assessment_service.update_assessment(email, assessment_id, update_data)
            
            logger.info(f"Updated assessment {assessment_id} with answers for user: {email}")
            
            return {
                "assessmentId": assessment_id,
                "status": "COMPLETED",
                "answers": answers,
                "score": updated_assessment.score,
                "percentageScore": float(updated_assessment.percentage_score) if updated_assessment.percentage_score else None,
                "isPassed": updated_assessment.is_passed,
                "updatedAt": updated_assessment.updated_at
            }
            
        except Exception as e:
            logger.error(f"Error updating assessment {assessment_id} for {email}: {e}")
            raise RuntimeError(f"Failed to update assessment: {e}")


# ============================================================================
# Service Factory Dependencies
# ============================================================================

def get_roadmap_service() -> NewRoadmapService:
    """
    Get roadmap service instance using new schema.
    
    Returns:
        NewRoadmapService instance
    """
    return NewRoadmapService()
