"""
Progress tracking service for roadmap assessments.

Handles progress calculation, analytics, and reporting
for roadmap-based learning journeys.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal

from ...utils.database import get_dynamodb_table
from ...utils.errorHandler import get_logger
from ...models.new_schema.assessment_model import Assessment, AssessmentStatus
from ...models.new_schema.roadmap_model import Roadmap
from .roadmap_service import get_new_roadmap_service
from .assessment_service import get_new_assessment_service

logger = get_logger(__name__)


class ProgressTrackingService:
    """Service for tracking roadmap progress and analytics."""
    
    def __init__(self):
        self.table = get_dynamodb_table("assessments")
        self.roadmap_service = get_new_roadmap_service()
        self.assessment_service = get_new_assessment_service()
        logger.info("ProgressTrackingService initialized")
    
    def get_roadmap_progress(self, email: str, roadmap_id: str) -> Dict[str, Any]:
        """
        Get overall progress for a roadmap.
        
        Args:
            email: User email
            roadmap_id: Roadmap ID
            
        Returns:
            Dict: Complete progress data
        """
        try:
            # Get roadmap data
            roadmap = self.roadmap_service.get_roadmap_by_id(email, roadmap_id)
            
            if not roadmap:
                raise RuntimeError(f"Roadmap {roadmap_id} not found")
            
            roadmap_data = roadmap.get_detailed_roadmap()
            if not roadmap_data:
                raise RuntimeError(f"Roadmap {roadmap_id} does not have detailed roadmap data")
            
            # Get all assessments for this roadmap
            assessments = self.assessment_service.get_roadmap_assessments(email, roadmap_id)
            
            # Get completion statistics
            completion_stats = self._calculate_completion_stats(assessments)
            
            progress_data = {
                "roadmap_id": roadmap_id,
                "career_title": roadmap_data.get("careerTitle", "Unknown Career"),
                "completion_stats": completion_stats,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Retrieved progress data for roadmap {roadmap_id}")
            
            return progress_data
            
        except Exception as e:
            logger.error(f"Error calculating roadmap progress: {e}")
            raise RuntimeError(f"Failed to calculate progress: {e}")
    
    def get_topic_progress(self, email: str, roadmap_id: str, topic_name: str) -> Dict[str, Any]:
        """
        Get progress for a specific topic.
        
        Args:
            email: User email
            roadmap_id: Roadmap ID
            topic_name: Topic name
            
        Returns:
            Dict: Topic progress data
        """
        try:
            # Get assessment for this topic
            assessment = self.assessment_service.get_assessment_by_roadmap_and_topic(
                email, roadmap_id, topic_name
            )
            
            if not assessment:
                raise RuntimeError(f"Assessment for topic {topic_name} not found")
            
            # Get roadmap data to find topic details
            roadmap = self.roadmap_service.get_roadmap_by_id(email, roadmap_id)
            if not roadmap:
                raise RuntimeError(f"Roadmap {roadmap_id} not found")
            
            roadmap_data = roadmap.get_detailed_roadmap()
            if not roadmap_data:
                raise RuntimeError(f"Roadmap {roadmap_id} does not have detailed roadmap data")
            
            topic_data = None
            for phase in roadmap_data.get("highLevelRoadmap", []):
                for topic in phase.get("topics", []):
                    if topic.get("topic") == topic_name:
                        topic_data = {
                            "topic": topic,
                            "phase": phase.get("phase"),
                            "phase_description": phase.get("description", "")
                        }
                        break
            
            topic_progress = {
                "topic_name": topic_name,
                "phase": assessment.phase,
                "status": self._get_topic_status(assessment),
                "assessment_id": assessment.assessment_id,
                "score": assessment.percentage_score,
                "is_passed": assessment.is_passed,
                "total_questions": assessment.total_questions,
                "questions_answered": assessment.questions_answered,
                "progress_percentage": assessment.get_progress_percentage(),
                "created_at": assessment.created_at,
                "started_at": assessment.started_at,
                "completed_at": assessment.completed_at,
                "evaluation": assessment.get_evaluation(),
                "skill_gaps": assessment.skill_gaps_identified,
                "strengths": assessment.strengths_identified,
                "recommendations": assessment.recommendations,
                "topic_data": topic_data
            }
            
            logger.info(f"Retrieved progress for topic {topic_name}")
            
            return topic_progress
            
        except Exception as e:
            logger.error(f"Error getting topic progress: {e}")
            raise RuntimeError(f"Failed to get topic progress: {e}")
    
    def update_progress(self, email: str, roadmap_id: str) -> Dict[str, Any]:
        """
        Recalculate and update progress for a roadmap.
        
        Args:
            email: User email
            roadmap_id: Roadmap ID
            
        Returns:
            Dict: Updated progress data
        """
        try:
            # Recalculate progress
            progress_data = self.get_roadmap_progress(email, roadmap_id)
            
            # Update roadmap with progress data (if needed)
            # This could involve updating a progress cache or summary table
            
            logger.info(f"Updated progress for roadmap {roadmap_id}")
            
            return progress_data
            
        except Exception as e:
            logger.error(f"Error updating progress: {e}")
            raise RuntimeError(f"Failed to update progress: {e}")
    
    
    def _calculate_completion_stats(self, assessments: List[Assessment]) -> Dict[str, Any]:
        """Calculate completion statistics."""
        total_assessments = len(assessments)
        completed_assessments = len([a for a in assessments if a.status == AssessmentStatus.COMPLETED.value])
        passed_assessments = len([a for a in assessments if a.is_passed])
        
        # Calculate average score
        scores = [float(a.percentage_score) for a in assessments if a.percentage_score is not None]
        average_score = sum(scores) / len(scores) if scores else 0.0
        
        return {
            "total_assessments": total_assessments,
            "completed_assessments": completed_assessments,
            "passed_assessments": passed_assessments,
            "completion_rate": round((completed_assessments / total_assessments * 100), 2) if total_assessments > 0 else 0.0,
            "pass_rate": round((passed_assessments / total_assessments * 100), 2) if total_assessments > 0 else 0.0,
            "average_score": round(average_score, 2)
        }
    


# ============================================================================
# Dependency Injection
# ============================================================================

_progress_tracking_service: Optional[ProgressTrackingService] = None

def get_progress_tracking_service() -> ProgressTrackingService:
    """
    Get or create ProgressTrackingService instance (singleton pattern).
    
    Returns:
        ProgressTrackingService instance
    """
    global _progress_tracking_service
    if _progress_tracking_service is None:
        _progress_tracking_service = ProgressTrackingService()
    return _progress_tracking_service
