"""
Roadmap Assessment API routes.

Handles assessment generation, evaluation, and progress tracking
for roadmap-integrated assessments.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Dict, Any, Optional

from ..services.new_schema.assessment_service import get_new_assessment_service
from ..services.new_schema.progress_service import get_progress_tracking_service
from ..services.new_schema.roadmap_service import get_new_roadmap_service
from ..schemas.common import success_response, error_response
from ..utils.errorHandler import get_logger
from ..models.enums import JourneyStage
from ..models.userModel import User
from ..services.new_userServices import get_current_active_user

logger = get_logger(__name__)

router = APIRouter()


# ============================================================================
# Assessment Generation APIs
# ============================================================================

@router.post(
    "/roadmap/topic",
    summary="Generate Assessment for Specific Topic",
    description="Generate assessment questions for a specific roadmap topic",
    status_code=status.HTTP_200_OK,
    tags=["Roadmap Assessments"]
)
async def generate_topic_assessment(
    request: Dict[str, Any] = Body(..., description="Topic assessment request"),
    current_user: User = Depends(get_current_active_user)
):
    """Generate assessment questions for a specific roadmap topic."""
    try:
        roadmap_id = request.get("roadmap_id")
        topic_name = request.get("topic_name")
        phase = request.get("phase")
        
        if not roadmap_id or not topic_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="roadmap_id and topic_name are required"
            )
        
        # Get user profile
        user_profile = current_user.to_dict()
        
        # Get assessment service
        assessment_service = get_new_assessment_service()
        
        # Generate assessment
        assessment_data = assessment_service.generate_topic_assessment(
            email=current_user.email,
            roadmap_id=roadmap_id,
            topic_name=topic_name,
            user_profile=user_profile
        )
        
        logger.info(f"Generated assessment for topic {topic_name} in roadmap {roadmap_id}")
        
        return success_response(
            data=assessment_data,
            message=f"Assessment generated successfully for {topic_name}",
            code=200
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating topic assessment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate assessment: {str(e)}"
        )



# ============================================================================
# Assessment Evaluation APIs
# ============================================================================

@router.post(
    "/roadmap/evaluate",
    summary="Evaluate Roadmap Assessment",
    description="Evaluate user answers for a roadmap assessment",
    status_code=status.HTTP_200_OK,
    tags=["Roadmap Assessments"]
)
async def evaluate_roadmap_assessment(
    request: Dict[str, Any] = Body(..., description="Assessment evaluation request"),
    current_user: User = Depends(get_current_active_user)
):
    """Evaluate user answers for a roadmap assessment."""
    try:
        assessment_id = request.get("assessment_id")
        user_answers = request.get("user_answers", [])
        
        if not assessment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="assessment_id is required"
            )
        
        if not user_answers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_answers are required"
            )
        
        # Get assessment service
        assessment_service = get_new_assessment_service()
        
        # Evaluate assessment
        evaluation_result = assessment_service.evaluate_roadmap_assessment(
            assessment_id=assessment_id,
            user_answers=user_answers
        )
        
        logger.info(f"Evaluated assessment {assessment_id}")
        
        return success_response(
            data=evaluation_result,
            message="Assessment evaluated successfully",
            code=200
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating assessment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate assessment: {str(e)}"
        )


# ============================================================================
# Progress Tracking APIs
# ============================================================================

@router.get(
    "/progress/roadmap/{roadmap_id}",
    summary="Get Roadmap Progress",
    description="Get overall progress for a roadmap",
    status_code=status.HTTP_200_OK,
    tags=["Progress Tracking"]
)
async def get_roadmap_progress(
    roadmap_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get overall progress for a roadmap."""
    try:
        # Get progress service
        progress_service = get_progress_tracking_service()
        
        # Calculate progress
        progress_data = progress_service.get_roadmap_progress(
            email=current_user.email,
            roadmap_id=roadmap_id
        )
        
        logger.info(f"Retrieved progress for roadmap {roadmap_id}")
        
        return success_response(
            data=progress_data,
            message="Roadmap progress retrieved successfully",
            code=200
        )
        
    except Exception as e:
        logger.error(f"Error getting roadmap progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get roadmap progress: {str(e)}"
        )



# ============================================================================
# Assessment Management APIs
# ============================================================================

@router.get(
    "/roadmap/{roadmap_id}",
    summary="Get Roadmap Assessments",
    description="Get all assessments for a roadmap",
    status_code=status.HTTP_200_OK,
    tags=["Assessment Management"]
)
async def get_roadmap_assessments(
    roadmap_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get all assessments for a roadmap."""
    try:
        # Get assessment service
        assessment_service = get_new_assessment_service()
        
        # Get assessments
        assessments = assessment_service.get_roadmap_assessments(
            email=current_user.email,
            roadmap_id=roadmap_id
        )
        
        # Convert to summary format
        assessment_summaries = [assessment.get_assessment_summary() for assessment in assessments]
        
        logger.info(f"Retrieved {len(assessments)} assessments for roadmap {roadmap_id}")
        
        return success_response(
            data={
                "roadmap_id": roadmap_id,
                "total_assessments": len(assessments),
                "assessments": assessment_summaries
            },
            message="Roadmap assessments retrieved successfully",
            code=200
        )
        
    except Exception as e:
        logger.error(f"Error getting roadmap assessments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get roadmap assessments: {str(e)}"
        )

