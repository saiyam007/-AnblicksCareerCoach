"""
Assessment Routes

API endpoints for assessment question generation and answer evaluation.
"""
from fastapi import APIRouter, HTTPException, status, Body
from ..schemas.assessment import (
    UserProfile,
    AssessmentQuestion,
    ResponseItem,
    EvaluationRequest,
    AssessmentQuestionResponse,
    EvaluationResponse
)
from ..services.assessmentService import get_assessment_service
from ..schemas.common import success_response
from ..utils.errorHandler import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/assessment/generate-questions",
    response_model=AssessmentQuestionResponse,
    summary="Generate Assessment Questions",
    description="Generate 5 assessment questions for a specific skill based on user profile",
    response_description="List of 5 assessment questions with varying difficulty levels",
    status_code=status.HTTP_200_OK,
    tags=["Assessment"]
)
async def generate_assessment_questions(
    profile: UserProfile = Body(..., description="User profile and skill details")
):
    """
    Generate 5 assessment questions for a specific skill.
    
    - **name**: User's name
    - **career_goal**: User's career goal
    - **skill**: Skill to be assessed
    - **experience**: User's experience level (optional)
    
    Returns 5 questions with:
    - 70% medium difficulty
    - 30% hard difficulty
    - Mix of MCQ and theory questions
    """
    logger.info(f"Generating assessment questions for user: {profile.name}, skill: {profile.skill}")
    
    try:
        assessment_service = get_assessment_service()
        
        # Convert Pydantic model to dict
        profile_data = profile.model_dump()
        
        # Generate questions
        questions = assessment_service.generate_questions(profile_data)
        
        logger.info(f"Successfully generated {len(questions)} assessment questions")
        
        # Return standardized response
        return success_response(
            data=questions,
            message=f"Assessment questions generated successfully for {profile.skill}",
            code=200
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error generating assessment questions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while generating assessment questions: {str(e)}"
        )


@router.post(
    "/assessment/evaluate",
    response_model=EvaluationResponse,
    summary="Evaluate Assessment Answers",
    description="Evaluate user's assessment responses and generate scores with detailed feedback",
    response_description="Evaluation results with scores, percentages, and summary",
    status_code=status.HTTP_200_OK,
    tags=["Assessment"]
)
async def evaluate_assessment_answers(
    request: EvaluationRequest = Body(..., description="User's responses to assessment questions")
):
    """
    Evaluate user's assessment responses and generate scores.
    
    - **responses**: List of user responses with question ID, skill, question text, difficulty, and user's answer
    
    Returns evaluation results with:
    - Total questions and correct answers
    - Intermediate score (medium difficulty)
    - Advanced score (hard difficulty)
    - Theory question score
    - Overall score
    - Summary feedback (2-5 points)
    """
    logger.info(f"Evaluating assessment responses for {len(request.responses)} questions")
    
    # Validate request
    if not request.responses or len(request.responses) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one response is required"
        )
    
    try:
        assessment_service = get_assessment_service()
        
        # Convert Pydantic models to dicts
        responses_data = [response.model_dump() for response in request.responses]
        
        # Evaluate answers
        evaluation_result = assessment_service.evaluate_answers(responses_data)
        
        logger.info(f"Assessment evaluation completed successfully")
        
        # Update assessment record in database if assessment_id is provided
        if hasattr(request, 'assessment_id') and request.assessment_id:
            try:
                from ..services.new_schema.assessment_service import NewAssessmentService
                assessment_service = NewAssessmentService()
                
                # Update assessment with evaluation results
                assessment_service.update_assessment_evaluation(
                    assessment_id=request.assessment_id,
                    evaluation_result=evaluation_result,
                    user_answers=responses_data
                )
                
                # Update roadmap progress if assessment is linked to roadmap
                try:
                    from ..agents.detailedRoadmapService import DetailedRoadmapService
                    roadmap_service = DetailedRoadmapService()
                    
                    # Get assessment details to find roadmap_id and topic_name
                    assessment_details = assessment_service.get_assessment_by_id(request.assessment_id)
                    if assessment_details and assessment_details.roadmap_id:
                        # Get the actual roadmap data from the roadmap service
                        from ..services.new_schema.roadmap_service import NewRoadmapService
                        roadmap_service_new = NewRoadmapService()
                        roadmap_data = roadmap_service_new.get_roadmap_by_id(assessment_details.email, assessment_details.roadmap_id)
                        
                        if roadmap_data:
                            # Convert Roadmap object to dictionary
                            roadmap_dict = roadmap_data.to_dict()
                            
                            # Parse detailed_roadmap if it's a JSON string
                            detailed_roadmap = roadmap_dict.get('detailed_roadmap', {})
                            if isinstance(detailed_roadmap, str):
                                import json
                                try:
                                    detailed_roadmap = json.loads(detailed_roadmap)
                                except json.JSONDecodeError as e:
                                    logger.error(f"Failed to parse detailed_roadmap JSON: {e}")
                                    detailed_roadmap = {}
                            
                            # Update roadmap topic progress
                            updated_roadmap = roadmap_service.update_topic_progress(
                                roadmap_data=detailed_roadmap,
                                topic_name=assessment_details.topic_name,
                                correct_answers=evaluation_result.get('Correct_Answers', 0),
                                total_questions=evaluation_result.get('Total_Questions', 0)
                            )
                            
                            # Save updated roadmap back to database
                            roadmap_service_new.set_detailed_roadmap(
                                email=assessment_details.email,
                                detailed_roadmap=updated_roadmap
                            )
                            logger.info(f"Updated roadmap progress for topic: {assessment_details.topic_name}")
                        else:
                            logger.warning(f"Could not retrieve roadmap data for roadmap_id: {assessment_details.roadmap_id}")
                except Exception as roadmap_error:
                    logger.warning(f"Failed to update roadmap progress: {roadmap_error}")
                
                logger.info(f"Updated assessment {request.assessment_id} with evaluation results")
            except Exception as e:
                logger.warning(f"Failed to update assessment record: {e}")
        
        # Return standardized response
        return success_response(
            data=evaluation_result,
            message="Assessment evaluated successfully",
            code=200
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error evaluating assessment answers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while evaluating assessment answers: {str(e)}"
        )

