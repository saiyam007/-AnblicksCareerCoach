"""
Assessment service for roadmap-integrated assessments.

Handles assessment creation, management, and progress tracking
with roadmap integration.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal

from ...utils.database import get_dynamodb_table
from ...utils.errorHandler import get_logger
from ...models.new_schema.assessment_model import Assessment, AssessmentStatus, AssessmentType
from ...models.new_schema.roadmap_model import Roadmap
from ...services.assessmentService import AssessmentService
from boto3.dynamodb.conditions import Attr

logger = get_logger(__name__)


class NewAssessmentService:
    """Service for roadmap-integrated assessments."""
    
    def __init__(self):
        self.table = get_dynamodb_table("assessments")
        self.assessment_service = AssessmentService()  # Use existing assessment service
        logger.info("NewAssessmentService initialized")
    
    def create_roadmap_assessment_record(self, email: str, roadmap_id: str, topic_name: str, 
                                       phase: str, assessment_order: int = 1, 
                                       is_required: bool = True, prerequisites: List[str] = None) -> Dict:
        """
        Create assessment record for a roadmap topic (without generating questions yet).
        
        Args:
            email: User email
            roadmap_id: Roadmap ID
            topic_name: Topic name from roadmap
            phase: Phase (now "General" for all topics)
            assessment_order: Order within roadmap
            is_required: Whether assessment is mandatory
            prerequisites: Required completed assessments
            
        Returns:
            Dict: Created assessment data
        """
        try:
            assessment = Assessment(
                email=email,
                title=f"Assessment: {topic_name}",
                description=f"Assessment for {topic_name}",
                assessment_type=AssessmentType.SKILL_BASED.value,
                skill_name=topic_name,  # Use topic_name as skill_name for existing GSI compatibility
                status=AssessmentStatus.CREATED.value,
                roadmap_id=roadmap_id,
                topic_name=topic_name,
                phase=phase,
                assessment_order=assessment_order,
                is_required=is_required,
                prerequisites=prerequisites or []
            )
            
            # Save to database
            self.table.put_item(Item=assessment.to_dict())
            
            logger.info(f"Created assessment record for {topic_name} in roadmap {roadmap_id}")
            
            return {
                "assessment_id": assessment.assessment_id,
                "title": assessment.title,
                "topic_name": topic_name,
                "phase": phase,
                "assessment_order": assessment_order,
                "status": assessment.status,
                "is_required": is_required,
                "created_at": assessment.created_at
            }
            
        except Exception as e:
            logger.error(f"Error creating assessment record: {e}")
            raise RuntimeError(f"Failed to create assessment record: {e}")
    
    def generate_topic_assessment(self, email: str, roadmap_id: str, topic_name: str, 
                                user_profile: Dict) -> Dict:
        """
        Generate assessment questions for a specific roadmap topic.
        
        Args:
            email: User email
            roadmap_id: Roadmap ID
            topic_name: Topic name from roadmap
            user_profile: User profile data
            
        Returns:
            Dict: Generated assessment with questions
        """
        try:
            # Get or create assessment record
            assessment = self.get_assessment_by_roadmap_and_topic(email, roadmap_id, topic_name)
            
            if not assessment:
                raise RuntimeError(f"Assessment record not found for topic {topic_name}")
            
            # Map to existing assessment API format
            assessment_request = {
                "career_goal": self._get_career_goal_from_roadmap(roadmap_id),
                "experience": user_profile.get("years_of_experience", "0 years"),
                "name": user_profile.get("full_name", "User"),
                "skill": topic_name
            }
            
            # Use existing assessment service to generate questions
            questions = self.assessment_service.generate_questions(assessment_request)
            
            # Update assessment with questions
            assessment.set_questions(questions)
            assessment.status = AssessmentStatus.CREATED.value  # Ready for taking
            
            # Save updated assessment
            self.table.put_item(Item=assessment.to_dict())
            
            logger.info(f"Generated assessment questions for {topic_name} in roadmap {roadmap_id}")
            
            return {
                "assessment_id": assessment.assessment_id,
                "topic_name": topic_name,
                "phase": assessment.phase,
                "questions": questions,
                "total_questions": len(questions),
                "status": assessment.status
            }
            
        except Exception as e:
            logger.error(f"Error generating topic assessment: {e}")
            raise RuntimeError(f"Failed to generate assessment: {e}")
    
    def update_assessment_evaluation(self, assessment_id: str, evaluation_result: Dict[str, Any], 
                                   user_answers: List[Dict[str, Any]]) -> Dict:
        """
        Update assessment with evaluation results after user completes assessment.
        
        Args:
            assessment_id: Assessment ID to update
            evaluation_result: AI evaluation results
            user_answers: User's submitted answers
            
        Returns:
            Dict: Updated assessment data
        """
        try:
            # Get existing assessment - need to scan since we only have assessment_id
            response = self.table.scan(
                FilterExpression=Attr('assessment_id').eq(assessment_id)
            )
            
            if not response.get('Items'):
                raise ValueError(f"Assessment {assessment_id} not found")
            
            assessment_data = response['Items'][0]  # Get first match
            assessment = Assessment.from_dict(assessment_data)
            
            # Update assessment with evaluation results
            assessment.status = AssessmentStatus.COMPLETED.value
            assessment.user_answers = user_answers
            assessment.score = evaluation_result.get('Correct_Answers', 0)
            assessment.total_questions = evaluation_result.get('Total_Questions', 0)
            assessment.percentage_score = Decimal(str(float(evaluation_result.get('Overall', '0%').replace('%', ''))))
            assessment.is_passed = assessment.percentage_score >= 60.0
            assessment.evaluation = evaluation_result
            assessment.completed_at = datetime.utcnow().isoformat()
            assessment.updated_at = datetime.utcnow().isoformat()
            
            # Save updated assessment
            self.table.put_item(Item=assessment.to_dict())
            
            logger.info(f"Updated assessment {assessment_id} with evaluation results")
            
            return {
                "assessment_id": assessment_id,
                "status": assessment.status,
                "score": assessment.score,
                "percentage_score": assessment.percentage_score,
                "is_passed": assessment.is_passed,
                "completed_at": assessment.completed_at
            }
            
        except Exception as e:
            logger.error(f"Error updating assessment evaluation: {e}")
            raise RuntimeError(f"Failed to update assessment evaluation: {e}")
    
    def evaluate_roadmap_assessment(self, assessment_id: str, user_answers: List[Dict]) -> Dict:
        """
        Evaluate user answers for a roadmap assessment.
        
        Args:
            assessment_id: Assessment ID
            user_answers: User's answers
            
        Returns:
            Dict: Evaluation results
        """
        try:
            # Get assessment
            assessment = self.get_assessment_by_id(assessment_id)
            
            if not assessment:
                raise RuntimeError(f"Assessment {assessment_id} not found")
            
            # Prepare evaluation request for existing API
            evaluation_request = {
                "responses": [
                    {
                        "id": answer.get("question_id", idx),
                        "question": answer.get("question", ""),
                        "skill": assessment.topic_name,
                        "difficulty": answer.get("difficulty", "medium"),
                        "user_answer": answer.get("user_answer", "")
                    }
                    for idx, answer in enumerate(user_answers)
                ]
            }
            
            # Use existing evaluation API (expects list of response dicts)
            evaluation_result = self.assessment_service.evaluate_answers(
                evaluation_request["responses"]
            )
            
            # Update assessment with results
            assessment.set_evaluation(evaluation_result)
            
            # Parse score from evaluation result
            overall_score = self._parse_score_from_evaluation(evaluation_result)
            assessment.percentage_score = Decimal(str(overall_score))
            assessment.is_passed = overall_score >= 60.0  # 60% passing threshold
            assessment.status = AssessmentStatus.COMPLETED.value
            assessment.completed_at = datetime.utcnow().isoformat()
            
            # Save updated assessment
            self.table.put_item(Item=assessment.to_dict())
            
            logger.info(f"Evaluated assessment {assessment_id} - Score: {overall_score}%, Passed: {assessment.is_passed}")
            
            return {
                "assessment_id": assessment_id,
                "topic_name": assessment.topic_name,
                "phase": assessment.phase,
                "score": overall_score,
                "is_passed": assessment.is_passed,
                "evaluation": evaluation_result,
                "completed_at": assessment.completed_at
            }
            
        except Exception as e:
            logger.error(f"Error evaluating assessment: {e}")
            raise RuntimeError(f"Failed to evaluate assessment: {e}")
    
    def get_assessment_by_id(self, assessment_id: str) -> Optional[Assessment]:
        """Get assessment by ID."""
        try:
            # Query by GSI on assessment_id
            response = self.table.scan(
                FilterExpression="assessment_id = :assessment_id",
                ExpressionAttributeValues={":assessment_id": assessment_id}
            )
            
            items = response.get('Items', [])
            if items:
                return Assessment.from_dict(items[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting assessment by ID: {e}")
            return None
    
    def get_assessment_by_roadmap_and_topic(self, email: str, roadmap_id: str, topic_name: str) -> Optional[Assessment]:
        """Get assessment by roadmap and topic."""
        try:
            response = self.table.query(
                KeyConditionExpression="email = :email",
                FilterExpression="roadmap_id = :roadmap_id AND topic_name = :topic_name",
                ExpressionAttributeValues={
                    ":email": email,
                    ":roadmap_id": roadmap_id,
                    ":topic_name": topic_name
                }
            )
            
            items = response.get('Items', [])
            if items:
                return Assessment.from_dict(items[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting assessment by roadmap and topic: {e}")
            return None
    
    def get_roadmap_assessments(self, email: str, roadmap_id: str) -> List[Assessment]:
        """Get all assessments for a roadmap."""
        try:
            response = self.table.query(
                KeyConditionExpression="email = :email",
                FilterExpression="roadmap_id = :roadmap_id",
                ExpressionAttributeValues={
                    ":email": email,
                    ":roadmap_id": roadmap_id
                }
            )
            
            items = response.get('Items', [])
            return [Assessment.from_dict(item) for item in items]
            
        except Exception as e:
            logger.error(f"Error getting roadmap assessments: {e}")
            return []
    
    def get_pending_assessments(self, email: str, roadmap_id: str) -> List[Assessment]:
        """Get pending (not completed) assessments for a roadmap."""
        try:
            assessments = self.get_roadmap_assessments(email, roadmap_id)
            return [
                assessment for assessment in assessments 
                if assessment.status in [AssessmentStatus.CREATED.value, AssessmentStatus.IN_PROGRESS.value]
            ]
        except Exception as e:
            logger.error(f"Error getting pending assessments: {e}")
            return []
    
    def get_completed_assessments(self, email: str, roadmap_id: str) -> List[Assessment]:
        """Get completed assessments for a roadmap."""
        try:
            assessments = self.get_roadmap_assessments(email, roadmap_id)
            return [
                assessment for assessment in assessments 
                if assessment.status == AssessmentStatus.COMPLETED.value
            ]
        except Exception as e:
            logger.error(f"Error getting completed assessments: {e}")
            return []
    
    def create_assessments_for_roadmap(self, email: str, roadmap_id: str, roadmap_data: Dict) -> List[Dict]:
        """
        Create assessment records for all unique topics in a roadmap (one per topic, not per phase).
        
        Args:
            email: User email
            roadmap_id: Roadmap ID
            roadmap_data: Roadmap data with phases and topics
            
        Returns:
            List[Dict]: Created assessment records
        """
        try:
            # Defensive programming: ensure roadmap_data is a dictionary
            if hasattr(roadmap_data, 'get_detailed_roadmap'):
                # If it's a Roadmap object, get the detailed roadmap data
                roadmap_data = roadmap_data.get_detailed_roadmap()
            
            if not isinstance(roadmap_data, dict):
                logger.error(f"roadmap_data is not a dictionary: {type(roadmap_data)}")
                raise ValueError(f"roadmap_data must be a dictionary, got {type(roadmap_data)}")
            
            # Check existing assessments for this roadmap to avoid duplicates
            existing_assessments = self.get_roadmap_assessments(email, roadmap_id)
            existing_topics = {assessment.topic_name for assessment in existing_assessments}
            
            assessments_created = []
            assessment_order = len(existing_assessments) + 1
            unique_topics = set()  # Track unique topics to avoid duplicates
            
            # Collect all unique topics from all phases
            for phase in roadmap_data.get("highLevelRoadmap", []):
                phase_name = phase.get("phase")
                
                for topic in phase.get("topics", []):
                    topic_name = topic.get("topic")
                    
                    # Only create assessment if topic is unique and doesn't already exist
                    if topic_name and topic_name not in unique_topics and topic_name not in existing_topics:
                        unique_topics.add(topic_name)
                        
                        # Create assessment record (no phase-specific info)
                        assessment_data = self.create_roadmap_assessment_record(
                            email=email,
                            roadmap_id=roadmap_id,
                            topic_name=topic_name,
                            phase="General",  # Use "General" instead of specific phase
                            assessment_order=assessment_order,
                            is_required=True
                        )
                        
                        assessments_created.append(assessment_data)
                        assessment_order += 1
            
            if assessments_created:
                logger.info(f"Created {len(assessments_created)} new assessment records for roadmap {roadmap_id}")
            else:
                logger.info(f"No new assessment records needed for roadmap {roadmap_id} - all topics already have assessments")
            
            return assessments_created
            
        except Exception as e:
            logger.error(f"Error creating assessments for roadmap: {e}")
            raise RuntimeError(f"Failed to create assessments for roadmap: {e}")
    
    def delete_assessments_by_roadmap(self, email: str, roadmap_id: str) -> int:
        """
        Delete all assessment records for a specific roadmap.
        
        Args:
            email: User email
            roadmap_id: Roadmap ID
            
        Returns:
            int: Number of deleted assessment records
        """
        try:
            # Get all assessments for this roadmap
            assessments = self.get_roadmap_assessments(email, roadmap_id)
            
            deleted_count = 0
            
            for assessment in assessments:
                try:
                    # Delete assessment record
                    self.table.delete_item(
                        Key={
                            "email": assessment.email,
                            "assessment_id": assessment.assessment_id
                        }
                    )
                    deleted_count += 1
                    logger.info(f"Deleted assessment {assessment.assessment_id} for topic {assessment.topic_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to delete assessment {assessment.assessment_id}: {e}")
            
            logger.info(f"Deleted {deleted_count} assessment records for roadmap {roadmap_id}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting assessments for roadmap {roadmap_id}: {e}")
            return 0
    
    def _get_career_goal_from_roadmap(self, roadmap_id: str) -> str:
        """Get career goal from roadmap data."""
        try:
            # This would typically query the roadmap service
            # For now, return a default value
            return "Career Development"
        except Exception as e:
            logger.warning(f"Could not get career goal from roadmap: {e}")
            return "Career Development"
    
    def _parse_score_from_evaluation(self, evaluation_result: Dict) -> float:
        """Parse overall score from evaluation result."""
        try:
            # Try to extract overall score from evaluation result
            if isinstance(evaluation_result, dict):
                overall = evaluation_result.get("Overall", "0%")
                if isinstance(overall, str) and "%" in overall:
                    return float(overall.replace("%", ""))
                elif isinstance(overall, (int, float)):
                    return float(overall)
            
            # Fallback to intermediate score
            intermediate = evaluation_result.get("Intermidiate_score", "0%")
            if isinstance(intermediate, str) and "%" in intermediate:
                return float(intermediate.replace("%", ""))
            elif isinstance(intermediate, (int, float)):
                return float(intermediate)
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Could not parse score from evaluation: {e}")
            return 0.0


# ============================================================================
# Dependency Injection
# ============================================================================

_new_assessment_service: Optional[NewAssessmentService] = None

def get_new_assessment_service() -> NewAssessmentService:
    """
    Get or create NewAssessmentService instance (singleton pattern).
    
    Returns:
        NewAssessmentService instance
    """
    global _new_assessment_service
    if _new_assessment_service is None:
        _new_assessment_service = NewAssessmentService()
    return _new_assessment_service