"""
Transformation Service for API compatibility.

This service provides transformation functions to convert between old and new schema formats,
ensuring API responses remain identical while using the new normalized database structure.
"""

from datetime import datetime
from typing import Any, Optional, Dict, List
import json

from ..utils.errorHandler import get_logger
from ..services.new_schema.user_service import get_new_user_service

logger = get_logger(__name__)


class TransformationService:
    """
    Service for transforming data between old and new schemas.
    
    Provides backward compatibility by:
    - Converting new normalized data to legacy API format
    - Maintaining identical response structures
    - Supporting gradual migration
    """
    
    def __init__(self):
        """Initialize transformation service."""
        self.new_user_service = get_new_user_service()
        logger.info("TransformationService initialized")
    
    def transform_user_to_legacy_format(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform new user data to legacy API format.
        
        Args:
            user_data: New user data from normalized schema
            
        Returns:
            Legacy format user data
        """
        try:
            # Map new schema fields to legacy format
            legacy_user = {
                'email': user_data.get('email'),
                'full_name': user_data.get('full_name'),
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'phone_number': user_data.get('phone_number'),
                'id': user_data.get('id'),
                'auth_provider': user_data.get('auth_provider'),
                'profile_picture_url': user_data.get('profile_picture_url'),
                'is_active': user_data.get('is_active'),
                'is_verified': user_data.get('is_verified'),
                'status': user_data.get('status'),
                'role': user_data.get('role'),
                'created_at': user_data.get('created_at'),
                'last_login_at': user_data.get('last_login_at')
            }
            
            # Remove None values to match legacy behavior
            return {k: v for k, v in legacy_user.items() if v is not None}
            
        except Exception as e:
            logger.error(f"Error transforming user to legacy format: {e}")
            return user_data
    
    def transform_profile_to_legacy_format(self, user_data: Dict[str, Any], profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform new user + profile data to legacy API format.
        
        Args:
            user_data: New user data from normalized schema
            profile_data: New profile data from normalized schema
            
        Returns:
            Legacy format combined user+profile data
        """
        try:
            # Start with user data
            legacy_data = self.transform_user_to_legacy_format(user_data)
            
            # Add profile-specific fields (these were in the old Users table)
            profile_fields = {
                'country': profile_data.get('country'),
                'state': profile_data.get('state'),
                'city': profile_data.get('city'),
                'userType': profile_data.get('user_type'),
                'careerGoal': profile_data.get('career_goal'),
                'lookingFor': profile_data.get('looking_for'),
                'languagePreference': profile_data.get('language_preference'),
                'currentEducationLevel': profile_data.get('current_education_level'),
                'fieldOfStudy': profile_data.get('field_of_study'),
                'academicInterests': profile_data.get('academic_interests'),
                'preferredStudyDestination': profile_data.get('preferred_study_destination'),
                'currentJobTitle': profile_data.get('current_job_title'),
                'industry': profile_data.get('industry'),
                'yearsOfExperience': profile_data.get('years_of_experience'),
                'currentCompany': profile_data.get('current_company'),
                'profile_summary': profile_data.get('profile_summary'),
                'recordId': 'PROFILE#LATEST',  # Legacy field for compatibility
                'updatedAt': profile_data.get('updated_at')
            }
            
            # Merge profile fields
            legacy_data.update(profile_fields)
            
            # Remove None values
            return {k: v for k, v in legacy_data.items() if v is not None}
            
        except Exception as e:
            logger.error(f"Error transforming profile to legacy format: {e}")
            return user_data
    
    def transform_roadmap_to_legacy_format(self, roadmap_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform new roadmap data to legacy API format.
        
        Args:
            roadmap_data: New roadmap data from normalized schema
            
        Returns:
            Legacy format roadmap data
        """
        try:
            # Legacy roadmap format
            legacy_roadmap = {
                'email': roadmap_data.get('email'),
                'roadmapId': roadmap_data.get('roadmap_id'),
                'status': roadmap_data.get('status'),
                'questions': roadmap_data.get('questions'),
                'answers': roadmap_data.get('answers'),
                'roadmap': roadmap_data.get('career_paths'),  # Map career_paths to roadmap
                'selectedCareerPath': roadmap_data.get('selected_career_path'),
                'detailedRoadmap': roadmap_data.get('detailed_roadmap'),
                'profile': roadmap_data.get('profile_snapshot'),
                'createdAt': roadmap_data.get('created_at'),
                'updatedAt': roadmap_data.get('updated_at')
            }
            
            # Remove None values
            return {k: v for k, v in legacy_roadmap.items() if v is not None}
            
        except Exception as e:
            logger.error(f"Error transforming roadmap to legacy format: {e}")
            return roadmap_data
    
    def transform_journey_to_legacy_format(self, journey_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform new journey data to legacy API format.
        
        Args:
            journey_data: New journey data from normalized schema
            
        Returns:
            Legacy format journey data
        """
        try:
            # Legacy journey format (this was embedded in user data before)
            legacy_journey = {
                'journey_stage': journey_data.get('current_stage'),
                'progress_percentage': journey_data.get('progress_percentage'),
                'completed_stages': journey_data.get('completed_stages'),
                'current_step': journey_data.get('current_step'),
                'total_steps': journey_data.get('total_steps'),
                'status': journey_data.get('status'),
                'is_active': journey_data.get('is_active'),
                'started_at': journey_data.get('started_at'),
                'last_activity_at': journey_data.get('last_activity_at'),
                'completed_at': journey_data.get('completed_at')
            }
            
            # Remove None values
            return {k: v for k, v in legacy_journey.items() if v is not None}
            
        except Exception as e:
            logger.error(f"Error transforming journey to legacy format: {e}")
            return journey_data
    
    def create_legacy_user_response(self, user_data: Dict[str, Any], profile_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a complete legacy user response.
        
        Args:
            user_data: New user data
            profile_data: New profile data (optional)
            
        Returns:
            Legacy format user response
        """
        try:
            if profile_data:
                # Combine user + profile data
                combined_data = self.transform_profile_to_legacy_format(user_data, profile_data)
            else:
                # Just user data
                combined_data = self.transform_user_to_legacy_format(user_data)
            
            # Create legacy response structure
            legacy_response = {
                'success': True,
                'message': 'User data retrieved successfully',
                'data': combined_data,
                'error': None,
                'code': 200
            }
            
            return legacy_response
            
        except Exception as e:
            logger.error(f"Error creating legacy user response: {e}")
            return {
                'success': False,
                'message': f'Error transforming user data: {str(e)}',
                'data': None,
                'error': str(e),
                'code': 500
            }
    
    def create_legacy_roadmap_response(self, roadmap_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a complete legacy roadmap response.
        
        Args:
            roadmap_data: New roadmap data
            
        Returns:
            Legacy format roadmap response
        """
        try:
            legacy_data = self.transform_roadmap_to_legacy_format(roadmap_data)
            
            # Create legacy response structure
            legacy_response = {
                'success': True,
                'message': 'Roadmap data retrieved successfully',
                'data': legacy_data,
                'error': None,
                'code': 200
            }
            
            return legacy_response
            
        except Exception as e:
            logger.error(f"Error creating legacy roadmap response: {e}")
            return {
                'success': False,
                'message': f'Error transforming roadmap data: {str(e)}',
                'data': None,
                'error': str(e),
                'code': 500
            }
    
    def create_legacy_state_response(self, user_data: Dict[str, Any], journey_data: Dict[str, Any], roadmap_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a complete legacy user state response.
        
        Args:
            user_data: New user data
            journey_data: New journey data
            roadmap_data: New roadmap data (optional)
            
        Returns:
            Legacy format user state response
        """
        try:
            # Transform user data
            legacy_user = self.transform_user_to_legacy_format(user_data)
            
            # Transform journey data
            legacy_journey = self.transform_journey_to_legacy_format(journey_data)
            
            # Merge journey fields into user data (legacy behavior)
            legacy_user.update(legacy_journey)
            
            # Add roadmap data if available
            current_data = {}
            if roadmap_data:
                legacy_roadmap = self.transform_roadmap_to_legacy_format(roadmap_data)
                current_data.update({
                    'questions': legacy_roadmap.get('questions'),
                    'answers': legacy_roadmap.get('answers'),
                    'roadmap': legacy_roadmap.get('roadmap'),
                    'roadmap_id': legacy_roadmap.get('roadmapId')
                })
            
            # Create legacy state response structure
            legacy_response = {
                'success': True,
                'message': f'User journey state retrieved successfully. Current stage: {legacy_journey.get("journey_stage")}',
                'data': {
                    'user': legacy_user,
                    'journey_stage': legacy_journey.get('journey_stage'),
                    'stage_info': {
                        'stage': legacy_journey.get('journey_stage'),
                        'is_valid': True
                    },
                    'progress': {
                        'current_step': legacy_journey.get('current_step'),
                        'total_steps': legacy_journey.get('total_steps'),
                        'progress_percentage': legacy_journey.get('progress_percentage'),
                        'completed_steps': legacy_journey.get('completed_stages', [])
                    },
                    'current_data': current_data
                },
                'error': None,
                'code': 200
            }
            
            return legacy_response
            
        except Exception as e:
            logger.error(f"Error creating legacy state response: {e}")
            return {
                'success': False,
                'message': f'Error transforming state data: {str(e)}',
                'data': None,
                'error': str(e),
                'code': 500
            }


# Dependency injection
_transformation_service: Optional[TransformationService] = None


def get_transformation_service() -> TransformationService:
    """
    Get or create TransformationService instance (singleton pattern).
    
    Returns:
        TransformationService instance
    """
    global _transformation_service
    if _transformation_service is None:
        _transformation_service = TransformationService()
    return _transformation_service
