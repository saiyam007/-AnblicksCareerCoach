"""
AI User Management Service Layer.

Business logic for AI Users table operations:
- User registration and updates
- User retrieval
- Profile summary updates
"""

from typing import Dict, List, Optional
from fastapi import HTTPException, status

from ..core.llmConnector import BedrockLLMClient
from ..utils.errorHandler import get_logger
from ..models.enums import JourneyStage
from .new_schema.user_service import get_new_user_service
from .new_schema.profile_service import get_user_profile_service
from .new_stageServices import get_stage_service

logger = get_logger(__name__)


class AIUserService:
    """Service class for AI User management business logic."""
    
    def __init__(self):
        """Initialize AI User service with new schema services and LLM client."""
        try:
            self.user_service = get_new_user_service()
            self.profile_service = get_user_profile_service()
            self.stage_service = get_stage_service()
            self.llm_client = BedrockLLMClient()
            logger.info("AIUserService initialized with new schema services")
        except Exception as e:
            logger.error(f"Failed to initialize AI User Service: {e}")
            raise
    
    # ============================================================================
    # User Registration & Updates
    # ============================================================================
    
    def register_user(self, user_data: Dict) -> Dict:
        """
        Register or update a user in the AI Users table.
        
        AUTOMATICALLY GENERATES AI profile summary and stores with user data.
        This combines registration + AI summary generation in one call.
        
        Args:
            user_data: User profile data from registration form
            
        Returns:
            Success response with user data including AI-generated summary
            
        Raises:
            HTTPException: If registration fails
        """
        try:
            # Validate required fields (firstName and lastName are optional)
            required_fields = ["email", "userType"]
            missing_fields = [field for field in required_fields if field not in user_data or not user_data[field]]
            
            if missing_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required fields: {', '.join(missing_fields)}"
                )
            
            logger.info(f"Registering user with AI summary: {user_data.get('email')}")
            
            # STEP 1: Generate AI profile summary automatically
            try:
                logger.info(" Generating AI profile summary...")
                summary_obj = self.llm_client.generate_profile_summary(user_data)
                
                if summary_obj and "summary" in summary_obj:
                    # Clean the summary text
                    profile_summary = summary_obj["summary"]
                    profile_summary = (
                        profile_summary
                        .replace(""", '"')
                        .replace(""", '"')
                        .replace("'", "")
                        .replace("\n", " ")
                        .strip()
                    )
                    user_data["profile_summary"] = profile_summary
                    logger.info(" AI summary generated and added to profile")
                else:
                    logger.warning("AI summary generation returned empty, continuing without it")
                    user_data["profile_summary"] = None
                    
            except Exception as ai_error:
                # Don't fail registration if AI fails, just log and continue
                logger.warning(f"AI summary generation failed: {ai_error}. Continuing without summary.")
                user_data["profile_summary"] = None
            
            # STEP 2: Save user and profile data using new schema
            email = user_data.get("email")
            
            # Create user record
            user_record = {
                "email": email,
                "full_name": f"{user_data.get('firstName', '')} {user_data.get('lastName', '')}".strip(),
                "first_name": user_data.get("firstName", ""),
                "last_name": user_data.get("lastName", ""),
                "status": "active",
                "auth_provider": "google"
            }
            
            # Create profile record
            profile_record = {
                "email": email,
                "career_goal": user_data.get("careerGoal"),
                "country": user_data.get("country"),
                "state": user_data.get("state"),
                "user_type": user_data.get("userType"),
                "looking_for": user_data.get("lookingFor"),
                "language_preference": user_data.get("languagePreference"),
                "current_education_level": user_data.get("currentEducationLevel"),
                "field_of_study": user_data.get("fieldOfStudy"),
                "academic_interests": user_data.get("academicInterests"),
                "preferred_study_destination": user_data.get("preferredStudyDestination"),
                "current_job_title": user_data.get("currentJobTitle"),
                "industry": user_data.get("industry"),
                "profile_summary": user_data.get("profile_summary")
            }
            
            # Save user and profile
            self.user_service.create_or_update_user(user_record)
            self.profile_service.create_or_update_profile(profile_record)
            
            logger.info(f"User registered successfully with AI summary: {email}")
            
            # STEP 3: Update user journey stage after successful profile completion
            stage_update_result = self.stage_service.update_user_stage(
                email=email,
                new_stage=JourneyStage.BASIC_REGISTERED
            )
            
            if stage_update_result.get("success"):
                logger.info(f"Updated user {user_data.get('email')} stage to BASIC_REGISTERED after profile completion")
            else:
                logger.warning(f"Failed to update stage for user {user_data.get('email')}: {stage_update_result.get('reason')}")
            
            return {
                "message": "User registered successfully",
                "user": user_data,
                "ai_summary_generated": user_data.get("profile_summary") is not None
            }
            
        except HTTPException:
            raise
        except RuntimeError as e:
            logger.exception(" Failed to register user")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error registering user: {str(e)}"
            )
        except Exception as e:
            logger.exception(" Unexpected error during registration")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred: {str(e)}"
            )
    
    # ============================================================================
    # User Retrieval
    # ============================================================================
    
    
    # ============================================================================
    # Profile Summary Updates
    # ============================================================================
    
    
    # ============================================================================
    # User Deletion
    # ============================================================================
    
    
    # ============================================================================
    # User Listing
    # ============================================================================
    


# ============================================================================
# Dependency Injection
# ============================================================================

# Global service instance
_ai_user_service = None

def get_ai_user_service() -> AIUserService:
    """
    Get or create AI User service instance (singleton pattern).
    
    Returns:
        AIUserService instance
    """
    global _ai_user_service
    if _ai_user_service is None:
        _ai_user_service = AIUserService()
    return _ai_user_service

