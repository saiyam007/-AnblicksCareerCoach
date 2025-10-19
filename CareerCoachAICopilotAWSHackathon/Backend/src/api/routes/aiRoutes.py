"""
AI-powered Career Advisor Routes.

Provides AI endpoints for:
- Generating career-specific questions
- Generating career roadmaps
- Generating profile summaries

These endpoints use AWS Bedrock (Claude 3.5 Sonnet) for intelligent responses.
"""

from fastapi import APIRouter, Body, status, Depends, HTTPException
from typing import List

# Import models
from ..models.userModel import User
from ..models.enums import JourneyStage

# Import schemas
from ..schemas.ai import (
    UserAnswer,
    StandardQuestionsResponse,
    StandardRoadmapResponse
)
from ..schemas.detailedRoadmap import DetailedRoadmapRequest, DetailedRoadmapResponse
from ..schemas.common import success_response

# Import service layer
from ..services.aiServices import get_ai_service
from ..services.new_userServices import get_current_active_user
from ..services.new_roadmapServices import get_roadmap_service
from ..services.new_stageServices import get_stage_service
from ..utils.errorHandler import get_logger

# Setup logging
logger = get_logger(__name__)

# Create router
router = APIRouter()

# Get service instance
ai_service = get_ai_service()


# ============================================================================
# AI Endpoints
# ============================================================================

@router.post(
    "/profile/questions",
    response_model=StandardQuestionsResponse,
    summary="Generate Questions for Authenticated User",
    description="Generate 3-5 career questions based on user's profile from database (User Journey Flow)",
    response_description="Standard response with 3-5 personalized questions",
    status_code=status.HTTP_200_OK,
    tags=["AI Career Advisor"]
)
async def generate_questions_for_user(
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate 3-5 career-specific questions for authenticated user.
    
    **Authentication Required:** User must be signed in (JWT token).
    
    **Smart Caching:** 
    - First checks if questions already exist in UserCareerRoadmaps table
    - Returns cached questions if found (no AI call needed)
    - Generates new questions only if none exist
    
    **User Journey Flow:**
    1. User completes basic registration → Stage: BASIC_REGISTERED
    2. User clicks "Continue" → This endpoint is called
    3. Backend checks for existing questions in UserCareerRoadmaps
    4. If questions exist: return cached questions
    5. If no questions: AI generates 3-5 personalized questions
    6. Questions saved to UserCareerRoadmaps table
    7. Stage remains: BASIC_REGISTERED (questions generated but not answered)
    8. Returns questions to frontend
    
    **Stage Update:** Stage will remain BASIC_REGISTERED until user answers questions.
    Once user submits answers via /profile/roadmap endpoint, stage will move to CAREER_PATHS_GENERATED.
    
    **No request body needed** - profile comes from database!
    
    **Response Format:**
    ```json
    {
        "success": true,
        "message": "Retrieved 5 career questions successfully",
        "data": {
            "questions": [
                {"id": "q1", "text": "..."},
                {"id": "q2", "text": "..."}
            ],
            "roadmapId": "550e8400-e29b-41d4-a716-446655440000"
        },
        "error": null,
        "code": 200
    }
    ```
    
    Returns:
        Standard response with 3-5 AI-generated questions and roadmapId
        
    Raises:
        HTTPException: If user has incomplete profile or AI fails
    """
    logger.info(f"Generating questions for authenticated user: {current_user.email}")
    
    # User data should already include profile information from authentication
    user_dict = current_user.to_dict()
    
    # Validate user has completed profile
    if not user_dict.get('careerGoal'):
        logger.warning(f"Profile incomplete - missing careerGoal for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User profile incomplete. Please complete registration first."
        )
    
    logger.info(f"Profile validation passed for user: {current_user.email}")
    
    # Convert user to profile dict
    profile_dict = current_user.to_dict()
    
    # NEW: Check if questions already exist in new schema
    roadmap_service = get_roadmap_service()
    
    existing_roadmap = roadmap_service.get_latest_roadmap(current_user.email)
    
    if existing_roadmap and existing_roadmap.get("questions") and existing_roadmap.get("status") == "QUESTIONS_GENERATED":
        # Questions already exist and roadmap is ready for answers - return from DB
        logger.info(f"Returning existing questions for user: {current_user.email}")
        questions = existing_roadmap["questions"]
        roadmap_id = existing_roadmap["roadmapId"]
    else:
        # No questions exist - generate new ones
        logger.info(f"Generating new questions for user: {current_user.email}")
        
        # Generate 3-5 questions (for user journey flow)
        questions = ai_service.generate_career_questions(profile_dict, max_questions=5)
        
        # Save questions to UserCareerRoadmaps
        roadmap_data = roadmap_service.save_questions_only(
            email=current_user.email,
            questions=questions,
            profile=profile_dict
        )
        roadmap_id = roadmap_data["roadmapId"]
    
    # Note: Stage remains BASIC_REGISTERED until user answers questions
    # Stage will be updated to PROFILE_COMPLETED/CAREER_PATHS_GENERATED 
        # when user submits answers via /profile/roadmap endpoint
        
    # Handle both AI response (dict) and DB response (JSON string)
    import json
    if isinstance(questions, str):
        try:
            questions = json.loads(questions)
        except json.JSONDecodeError:
            questions = []
    
    if isinstance(questions, dict):
        questions = questions.get("questions", [])
    elif not isinstance(questions, list):
        questions = []

    # Return standardized response with roadmapId
    return success_response(
        data={
            "questions": questions,
            "roadmapId": roadmap_id
        },
        message=f"Retrieved {len(questions)} career questions successfully",
        code=200
    )



@router.post(
    "/profile/roadmap",
    response_model=StandardRoadmapResponse,
    summary="Generate Roadmap for Authenticated User",
    description="Generate career roadmap using user's profile from DB + answers (User Journey Flow)",
    response_description="Standard response with personalized career paths",
    status_code=status.HTTP_200_OK,
    tags=["AI Career Advisor"]
)
async def generate_roadmap_for_user(
    answers: List[UserAnswer] = Body(..., description="User answers to questions"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate career roadmap for authenticated user.
    
    **Authentication Required:** User must be signed in (JWT token).
    
    **Enhanced User Journey Flow:**
    1. User answers 3-5 questions (from previous step)
    2. Frontend sends ONLY answers + JWT token
    3. Backend gets latest roadmap with questions from UserCareerRoadmaps
    4. Backend validates questions exist and are in QUESTIONS_GENERATED status
    5. Backend fetches user profile from DB (using email from JWT)
    6. AI analyzes profile + answers → generates roadmap
    7. Backend updates UserCareerRoadmaps with answers and roadmap
    8. Returns 3-5 career paths
    
    **Profile comes from database** - no need to send in request!
    **Questions must exist** - user must have generated questions first!
    
    **Response Format:**
    ```json
    {
        "success": true,
        "message": "Career roadmap generated successfully",
        "data": {
            "careerPaths": [
                {
                    "title": "ML Engineer",
                    "description": "...",
                    "timeToAchieve": "6-12 months",
                    "averageSalary": "...",
                    "keySkillsRequired": [...],
                    "learningRoadmap": [...],
                    "aiRecommendation": {...}
                }
            ]
        },
        "error": null,
        "code": 200
    }
    ```
    
    Args:
        answers: List of user answers (3-5 answers)
        current_user: Authenticated user (automatically fetched from DB)
        
    Returns:
        Standard response with career paths and roadmaps
        
    Raises:
        HTTPException: If profile incomplete, questions not found, or AI fails
    """
    logger.info(f"Generating roadmap for authenticated user: {current_user.email} with {len(answers)} answers")
    
    # NEW: Get latest roadmap with questions from new schema
    roadmap_service = get_roadmap_service()
    
    latest_roadmap = roadmap_service.get_latest_roadmap(current_user.email)
    
    # Debug: Log the roadmap status
    if latest_roadmap:
        logger.info(f"Latest roadmap status: {latest_roadmap.get('status')}")
        logger.info(f"Latest roadmap keys: {list(latest_roadmap.keys())}")
    
    if not latest_roadmap:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No questions found. Please generate questions first."
        )
    
    # Check if roadmap is in the right state for generating career paths
    roadmap_status = latest_roadmap.get("status")
    if roadmap_status == "CAREER_PATHS_GENERATED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Career paths already generated. Please generate new questions to create a new roadmap."
        )
    elif roadmap_status == "ROADMAP_COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Roadmap already completed. Please generate new questions to create a new roadmap."
        )
    elif roadmap_status != "QUESTIONS_GENERATED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No questions found. Please generate questions first."
        )
    
    roadmap_id = latest_roadmap["roadmapId"]
    
    # Validate user has completed profile
    if not current_user.to_dict().get('careerGoal'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User profile incomplete. Please complete registration first."
        )
    
    # Check if roadmap already exists (user resuming journey)
    if latest_roadmap.get("roadmap"):
        # Roadmap already exists - return from DB
        logger.info(f"Returning existing roadmap for user: {current_user.email}")
        roadmap = latest_roadmap["roadmap"]
        answers_list = latest_roadmap.get("answers", [])
    else:
        # No roadmap exists - generate new one
        logger.info(f"Generating new roadmap for user: {current_user.email}")
        
        # Get profile from authenticated user (from DB)
        profile_dict = current_user.to_dict()
        
        # Convert answers to dict list
        answers_list = [answer.model_dump() for answer in answers]
        
        # Generate roadmap using profile from DB + user answers
        roadmap = ai_service.generate_career_roadmap(profile_dict, answers_list)
        
        # Update UserCareerRoadmaps with answers and roadmap
        roadmap_service.update_with_roadmap(
            email=current_user.email,
            roadmap_id=roadmap_id,
            answers=answers_list,
            roadmap=roadmap
        )
    
    # Update user journey stage after successful roadmap generation
    # User has answered questions → Profile completed → Career paths available
    stage_service = get_stage_service()
    
    stage_update_result = stage_service.update_user_stage(
        email=current_user.email,
        new_stage=JourneyStage.CAREER_PATHS_GENERATED
    )
    
    if stage_update_result.get("success"):
        logger.info(f"Updated user {current_user.email} stage to CAREER_PATHS_GENERATED")
    else:
        logger.warning(f"Failed to update stage for user {current_user.email}: {stage_update_result.get('reason')}")
    
    # Return standardized response
    return success_response(
        data=roadmap,
        message=f"Career roadmap generated successfully with {len(roadmap.get('careerPaths', []))} paths",
        code=200
    )


# ============================================================================
# Detailed Roadmap Generation
# ============================================================================

@router.post(
    "/profile/detailed-roadmap",
    response_model=DetailedRoadmapResponse,
    summary="Generate Detailed Roadmap for Selected Career Path",
    description="Generate comprehensive detailed roadmap for user's selected career path",
    response_description="Complete detailed roadmap with phases, subtopics, resources, and projects",
    status_code=status.HTTP_200_OK,
    tags=["AI Career Advisor"]
)
async def generate_detailed_roadmap(
    request: DetailedRoadmapRequest = Body(..., description="Selected career path data"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate comprehensive detailed roadmap for user's selected career path.
    
    **Authentication Required:** User must be signed in (JWT token).
    
    **Enhanced User Journey Flow:**
    1. User selects a career path from the generated list
    2. Frontend sends selected career path data + JWT token
    3. Backend gets latest roadmap with questions/answers from UserCareerRoadmaps
    4. Backend validates user has completed previous steps
    5. AI generates comprehensive detailed roadmap using complete_roadmap_generation
    6. Backend stores detailed roadmap in UserCareerRoadmaps table
    7. Backend updates user journey stage to ROADMAP_GENERATED
    8. Returns complete detailed roadmap with phases, subtopics, resources, projects
    
    **Request Format:**
    ```json
    {
        "selectedCareerPath": {
            "title": "Computer Vision Engineer for Robotics",
            "description": "Specialize in developing vision systems...",
            "timeToAchieve": "1-2 years",
            "averageSalary": "₹12-24 LPA",
            "keySkillsRequired": [...]
        }
    }
    ```
    
    **Response Format:**
    ```json
    {
        "success": true,
        "message": "Detailed roadmap generated successfully",
        "data": {
            "careerTitle": "Computer Vision Engineer for Robotics",
            "highLevelRoadmap": [
                {
                    "phase": "Beginner",
                    "duration": "3-4 months",
                    "topics": [
                        {
                            "topic": "Python Programming Fundamentals",
                            "subtopics": [
                                "Python syntax and data types",
                                "Functions and modules",
                                "Object-oriented programming",
                                "File I/O and error handling"
                            ]
                        }
                    ],
                    "resources": [...],
                    "outcomes": [...]
                }
            ],
            "capstoneProjects": [...]
        },
        "error": null,
        "code": 200
    }
    ```
    
    Args:
        request: Selected career path data
        current_user: Authenticated user (automatically fetched from DB)
        
    Returns:
        Complete detailed roadmap with phases, subtopics, resources, and projects
        
    Raises:
        HTTPException: If user hasn't completed previous steps or AI fails
    """
    logger.info(f"Generating detailed roadmap for user: {current_user.email}")
    
    # Validate user has completed profile
    # if not current_user.to_dict().get('careerGoal'):
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="User profile incomplete. Please complete registration first."
    #     )
    

    # Get latest roadmap to check status instead of user stage
    roadmap_service = get_roadmap_service()
    latest_roadmap = roadmap_service.get_latest_roadmap(current_user.email)
    
    if not latest_roadmap:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No roadmap found. Please complete the career path generation first."
        )
    
    # Check if roadmap has career paths (should be CAREER_PATHS_GENERATED status)
    roadmap_status = latest_roadmap.get("status", "")
    if roadmap_status not in ['CAREER_PATHS_GENERATED', 'ROADMAP_COMPLETED']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid roadmap status: {roadmap_status}. Must have career paths generated first. Please complete the question answering and career path generation."
        )
    
    # latest_roadmap is already retrieved above
    
    roadmap_id = latest_roadmap["roadmapId"]
    selected_career_path = request.selectedCareerPath
    
    # Check if selectedCareerPath is empty - if so, return existing roadmap from database
    if not selected_career_path or selected_career_path == {}:
        logger.info(f"Empty selectedCareerPath payload for user: {current_user.email} - returning existing roadmap from database")
        
        # Check if detailed roadmap already exists in the latest roadmap
        existing_detailed_roadmap = latest_roadmap.get("detailedRoadmap")
        existing_selected_career_path = latest_roadmap.get("selectedCareerPath", {})
        
        if existing_detailed_roadmap and existing_selected_career_path:
            # Parse JSON string if needed
            import json
            if isinstance(existing_detailed_roadmap, str):
                try:
                    existing_detailed_roadmap = json.loads(existing_detailed_roadmap)
                except json.JSONDecodeError:
                    logger.error("Failed to parse existing detailed roadmap JSON")
                    existing_detailed_roadmap = None
            
            if existing_detailed_roadmap:
                # Add roadmapId to response
                response_data = existing_detailed_roadmap.copy()
                response_data["roadmapId"] = roadmap_id
                
                return success_response(
                    data=response_data,
                    message=f"Retrieved existing detailed roadmap for {existing_selected_career_path.get('title', 'Unknown Career')}",
                    code=200
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No existing detailed roadmap found. Please select a career path first."
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existing detailed roadmap found. Please select a career path first."
            )
    
    # Validate selected career path has required fields (only if not empty)
    required_fields = ["title", "description", "keySkillsRequired"]
    for field in required_fields:
        if field not in selected_career_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid career path data. Missing required field: {field}"
            )
    
    # ============================================================================
    # DETAILED ROADMAP CACHING LOGIC
    # ============================================================================
    
    # Check if detailed roadmap already exists for this career path
    existing_detailed_roadmap = latest_roadmap.get("detailedRoadmap")
    existing_selected_career_path = latest_roadmap.get("selectedCareerPath", {})
    
    # Compare career paths (check title match for caching)
    career_path_title_match = (
        existing_selected_career_path.get("title") == selected_career_path.get("title")
    )
    
    if existing_detailed_roadmap and career_path_title_match:
        # CACHE HIT: Return existing detailed roadmap
        logger.info(f"Cache hit: Returning existing detailed roadmap for career path: {selected_career_path['title']}")
        
        # Parse JSON string if needed
        import json
        if isinstance(existing_detailed_roadmap, str):
            try:
                existing_detailed_roadmap = json.loads(existing_detailed_roadmap)
            except json.JSONDecodeError:
                logger.error("Failed to parse existing detailed roadmap JSON")
                existing_detailed_roadmap = None
        
        if existing_detailed_roadmap:
            # Add roadmapId to cached response
            response_data = existing_detailed_roadmap.copy()
            response_data["roadmapId"] = roadmap_id
            
            return success_response(
                data=response_data,
                message=f"Retrieved cached detailed roadmap for {selected_career_path['title']}",
                code=200
            )
    
    # CACHE MISS: Generate new detailed roadmap
    logger.info(f"Cache miss: Generating new detailed roadmap for career path: {selected_career_path['title']}")
    
    # If career path changed, delete existing assessment records
    if existing_detailed_roadmap and not career_path_title_match:
        logger.info(f"Career path changed from '{existing_selected_career_path.get('title', 'Unknown')}' to '{selected_career_path['title']}' - deleting existing assessments")
        
        # Delete existing assessment records for this roadmap
        from ..services.new_schema.assessment_service import get_new_assessment_service
        assessment_service = get_new_assessment_service()
        
        try:
            deleted_count = assessment_service.delete_assessments_by_roadmap(current_user.email, roadmap_id)
            logger.info(f"Deleted {deleted_count} existing assessment records for roadmap {roadmap_id}")
        except Exception as e:
            logger.warning(f"Failed to delete existing assessments: {e}")
    
    try:
        # Prepare input payload for detailed roadmap generation
        input_payload = {
            "title": selected_career_path["title"],
            "description": selected_career_path["description"],
            "timeToAchieve": selected_career_path.get("timeToAchieve", "1-2 years"),
            "averageSalary": selected_career_path.get("averageSalary", ""),
            "keySkillsRequired": selected_career_path["keySkillsRequired"],
            "user_profile": current_user.to_dict()
        }
        
        logger.info(f"Generating new detailed roadmap for: {input_payload['title']}")
        
        # Generate detailed roadmap using Bedrock Agent
        from ..agents.detailedRoadmapService import get_detailed_roadmap_service
        
        detailed_roadmap_service = get_detailed_roadmap_service()
        detailed_roadmap = detailed_roadmap_service.generate_detailed_roadmap(input_payload)
        
        if not detailed_roadmap:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate detailed roadmap. Please try again."
            )
        
        # Store detailed roadmap and selected career path in UserCareerRoadmaps
        roadmap_service.update_with_detailed_roadmap(
            email=current_user.email,
            roadmap_id=roadmap_id,
            detailed_roadmap=detailed_roadmap,
            selected_career_path=selected_career_path
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating detailed roadmap: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while generating detailed roadmap: {str(e)}"
        )
    
    # Update user journey stage to ROADMAP_GENERATED
    stage_service = get_stage_service()
    
    stage_update_result = stage_service.update_user_stage(
        email=current_user.email,
        new_stage=JourneyStage.ROADMAP_GENERATED
    )
    
    if stage_update_result.get("success"):
        logger.info(f"Updated user {current_user.email} stage to ROADMAP_GENERATED")
    else:
        logger.warning(f"Failed to update stage for user {current_user.email}: {stage_update_result.get('reason')}")
    
    # Add roadmapId to new generation response
    response_data = detailed_roadmap.copy()
    response_data["roadmapId"] = roadmap_id
    
    # Return standardized response
    return success_response(
        data=response_data,
        message=f"Detailed roadmap generated successfully for {selected_career_path['title']}",
        code=200
    )


# ============================================================================
# Health Check for AI Service
# ============================================================================

@router.get(
    "/ai/health",
    summary="AI Service Health Check",
    description="Check if AWS Bedrock AI service is properly configured",
    response_description="AI service health status",
    status_code=status.HTTP_200_OK,
    tags=["AI Career Advisor"]
)
async def ai_health_check():
    """
    Check AI service health and configuration.
    
    Returns:
        Health status of AI service including configuration details
    """
    return ai_service.check_health()
