"""
User Profile Service for normalized user_profiles table.

Handles career profile data with versioning support.
"""

from datetime import datetime
from typing import Any, Optional, Dict, List
import uuid

from ...utils.database import get_dynamodb_table
from ...utils.errorHandler import get_logger
from ...models.new_schema.profile_model import UserProfile, UserType, EducationLevel

logger = get_logger(__name__)


class UserProfileService:
    """
    Service for managing user profiles in the normalized user_profiles table.
    
    Handles career profile data with versioning:
    - Profile creation and updates with versioning
    - Career context for AI processing
    - Skill gap analysis and recommendations
    - Profile history tracking
    """
    
    def __init__(self):
        """Initialize the service with user_profiles table."""
        self.table = get_dynamodb_table('user_profiles')
        logger.info("UserProfileService initialized with user_profiles table")
    
    def create_profile(self, email: str, profile_data: Dict[str, Any]) -> UserProfile:
        """
        Create a new user profile.
        
        Args:
            email: User email address
            profile_data: Profile data dictionary
            
        Returns:
            UserProfile: Created profile object
        """
        try:
            # Add email and set as current version
            profile_data['email'] = email
            profile_data['is_current'] = 'true'
            profile_data['profile_version'] = f"v{int(datetime.utcnow().timestamp())}"
            
            # Set timestamps
            profile_data['created_at'] = datetime.utcnow().isoformat()
            profile_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Create profile object
            profile = UserProfile(**profile_data)
            
            # Save to DynamoDB
            self.table.put_item(Item=profile.to_dict())
            
            logger.info(f"Created new profile for user: {email}")
            return profile
            
        except Exception as e:
            logger.error(f"Error creating profile for {email}: {e}")
            raise
    
    def create_or_update_profile(self, profile_data: Dict[str, Any]) -> UserProfile:
        """
        Create or update a profile (alias for create_profile for compatibility).
        
        Args:
            profile_data: Profile data dictionary (must contain 'email')
            
        Returns:
            UserProfile: Created profile object
        """
        email = profile_data.get('email')
        if not email:
            raise ValueError("Email is required for profile creation")
        return self.create_profile(email, profile_data)
    
    def get_current_profile(self, email: str) -> Optional[UserProfile]:
        """
        Get current profile for user using GSI.
        
        Args:
            email: User email address
            
        Returns:
            UserProfile or None if not found
        """
        try:
            response = self.table.query(
                IndexName='current-profiles-index',
                KeyConditionExpression='is_current = :current',
                FilterExpression='email = :email',
                ExpressionAttributeValues={
                    ':email': email,
                    ':current': 'true'
                },
                ScanIndexForward=False,  # Get most recent first
                Limit=1
            )
            
            if response['Items']:
                profile = UserProfile.from_dict(response['Items'][0])
                logger.info(f"Retrieved current profile for: {email}")
                return profile
            else:
                logger.info(f"No current profile found for: {email}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting current profile for {email}: {e}")
            raise
    
    def get_profile_by_version(self, email: str, version: str) -> Optional[UserProfile]:
        """
        Get specific profile version.
        
        Args:
            email: User email address
            version: Profile version (e.g., 'v1234567890')
            
        Returns:
            UserProfile or None if not found
        """
        try:
            response = self.table.get_item(
                Key={
                    'email': email,
                    'profile_version': version
                }
            )
            
            if 'Item' in response:
                profile = UserProfile.from_dict(response['Item'])
                logger.info(f"Retrieved profile version {version} for: {email}")
                return profile
            else:
                logger.info(f"Profile version {version} not found for: {email}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting profile version {version} for {email}: {e}")
            raise
    
    def get_profile_history(self, email: str, limit: int = 10) -> List[UserProfile]:
        """
        Get profile history for user.
        
        Args:
            email: User email address
            limit: Maximum number of versions to return
            
        Returns:
            List of UserProfile objects
        """
        try:
            response = self.table.query(
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={':email': email},
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )
            
            profiles = [UserProfile.from_dict(item) for item in response.get('Items', [])]
            logger.info(f"Retrieved {len(profiles)} profile versions for: {email}")
            return profiles
            
        except Exception as e:
            logger.error(f"Error getting profile history for {email}: {e}")
            raise
    
    def update_profile(self, email: str, updates: Dict[str, Any], create_new_version: bool = True) -> UserProfile:
        """
        Update user profile.
        
        Args:
            email: User email address
            updates: Dictionary of fields to update
            create_new_version: Whether to create a new version or update current
            
        Returns:
            Updated UserProfile
        """
        try:
            if create_new_version:
                # Get current profile
                current_profile = self.get_current_profile(email)
                if not current_profile:
                    raise ValueError(f"No current profile found for {email}")
                
                # Create new version
                new_profile = current_profile.create_new_version(updates)
                
                # Mark old version as not current
                self.table.update_item(
                    Key={
                        'email': email,
                        'profile_version': current_profile.profile_version
                    },
                    UpdateExpression='SET is_current = :current, updated_at = :update_time',
                    ExpressionAttributeValues={
                        ':current': 'false',
                        ':update_time': datetime.utcnow().isoformat()
                    }
                )
                
                # Save new version
                self.table.put_item(Item=new_profile.to_dict())
                
                logger.info(f"Created new profile version for: {email}")
                return new_profile
                
            else:
                # Update current version in place
                current_profile = self.get_current_profile(email)
                if not current_profile:
                    raise ValueError(f"No current profile found for {email}")
                
                # Build update expression
                update_expression = 'SET '
                expression_attribute_names = {}
                expression_attribute_values = {}
                
                for key, value in updates.items():
                    update_expression += f'#{key} = :{key}, '
                    expression_attribute_names[f'#{key}'] = key
                    expression_attribute_values[f':{key}'] = value
                
                # Add updated timestamp
                update_expression += 'updated_at = :update_time'
                expression_attribute_values[':update_time'] = datetime.utcnow().isoformat()
                
                response = self.table.update_item(
                    Key={
                        'email': email,
                        'profile_version': current_profile.profile_version
                    },
                    UpdateExpression=update_expression,
                    ExpressionAttributeNames=expression_attribute_names,
                    ExpressionAttributeValues=expression_attribute_values,
                    ReturnValues='ALL_NEW'
                )
                
                updated_profile = UserProfile.from_dict(response['Attributes'])
                logger.info(f"Updated profile for: {email}")
                return updated_profile
                
        except Exception as e:
            logger.error(f"Error updating profile for {email}: {e}")
            raise
    
    def complete_profile(self, email: str, completion_data: Dict[str, Any]) -> UserProfile:
        """
        Complete user profile with AI-generated summary.
        
        Args:
            email: User email address
            completion_data: Profile completion data including AI summary
            
        Returns:
            Completed UserProfile
        """
        try:
            # Update profile with completion data
            completion_data['is_complete'] = True
            completion_data['source'] = 'ai_completed'
            
            updated_profile = self.update_profile(email, completion_data, create_new_version=True)
            
            logger.info(f"Completed profile for: {email}")
            return updated_profile
            
        except Exception as e:
            logger.error(f"Error completing profile for {email}: {e}")
            raise
    
    def add_ai_insight(self, email: str, insight_type: str, insight_data: Any) -> bool:
        """
        Add AI-generated insight to current profile.
        
        Args:
            email: User email address
            insight_type: Type of insight (e.g., 'skill_gaps', 'recommendations')
            insight_data: Insight data
            
        Returns:
            True if successful
        """
        try:
            current_profile = self.get_current_profile(email)
            if not current_profile:
                logger.warning(f"No current profile found for {email}")
                return False
            
            # Add insight to current profile
            current_profile.add_ai_insight(insight_type, insight_data)
            
            # Update in database
            self.table.update_item(
                Key={
                    'email': email,
                    'profile_version': current_profile.profile_version
                },
                UpdateExpression='SET ai_insights = :insights, updated_at = :update_time',
                ExpressionAttributeValues={
                    ':insights': current_profile.ai_insights,
                    ':update_time': datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Added AI insight '{insight_type}' for: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding AI insight for {email}: {e}")
            return False
    
    def add_skill_gap(self, email: str, skill_gap: str) -> bool:
        """
        Add identified skill gap to current profile.
        
        Args:
            email: User email address
            skill_gap: Identified skill gap
            
        Returns:
            True if successful
        """
        try:
            current_profile = self.get_current_profile(email)
            if not current_profile:
                logger.warning(f"No current profile found for {email}")
                return False
            
            # Add skill gap to current profile
            current_profile.add_skill_gap(skill_gap)
            
            # Update in database
            self.table.update_item(
                Key={
                    'email': email,
                    'profile_version': current_profile.profile_version
                },
                UpdateExpression='SET skill_gaps = :gaps, updated_at = :update_time',
                ExpressionAttributeValues={
                    ':gaps': current_profile.skill_gaps,
                    ':update_time': datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Added skill gap '{skill_gap}' for: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding skill gap for {email}: {e}")
            return False
    
    def add_recommendation(self, email: str, recommendation: Dict[str, Any]) -> bool:
        """
        Add AI recommendation to current profile.
        
        Args:
            email: User email address
            recommendation: Recommendation data
            
        Returns:
            True if successful
        """
        try:
            current_profile = self.get_current_profile(email)
            if not current_profile:
                logger.warning(f"No current profile found for {email}")
                return False
            
            # Add recommendation to current profile
            current_profile.add_recommendation(recommendation)
            
            # Update in database
            self.table.update_item(
                Key={
                    'email': email,
                    'profile_version': current_profile.profile_version
                },
                UpdateExpression='SET recommendations = :recs, updated_at = :update_time',
                ExpressionAttributeValues={
                    ':recs': current_profile.recommendations,
                    ':update_time': datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Added recommendation for: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding recommendation for {email}: {e}")
            return False
    
    def get_career_context(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get career context for AI processing.
        
        Args:
            email: User email address
            
        Returns:
            Career context dictionary or None
        """
        try:
            current_profile = self.get_current_profile(email)
            if not current_profile:
                logger.warning(f"No current profile found for {email}")
                return None
            
            career_context = current_profile.get_career_context()
            logger.info(f"Retrieved career context for: {email}")
            return career_context
            
        except Exception as e:
            logger.error(f"Error getting career context for {email}: {e}")
            return None
    
    def profile_exists(self, email: str) -> bool:
        """
        Check if user has any profile.
        
        Args:
            email: User email address
            
        Returns:
            True if profile exists, False otherwise
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
            logger.error(f"Error checking if profile exists for {email}: {e}")
            return False
    
    def get_profile_summary(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get profile summary for API responses.
        
        Args:
            email: User email address
            
        Returns:
            Profile summary dictionary or None
        """
        try:
            current_profile = self.get_current_profile(email)
            if not current_profile:
                return None
            
            return {
                'email': current_profile.email,
                'profile_version': current_profile.profile_version,
                'user_type': current_profile.user_type,
                'career_goal': current_profile.career_goal,
                'country': current_profile.country,
                'state': current_profile.state,
                'current_education_level': current_profile.current_education_level,
                'field_of_study': current_profile.field_of_study,
                'academic_interests': current_profile.academic_interests,
                'current_job_title': current_profile.current_job_title,
                'industry': current_profile.industry,
                'years_of_experience': current_profile.years_of_experience,
                'is_complete': current_profile.is_complete,
                'profile_summary': current_profile.profile_summary,
                'created_at': current_profile.created_at,
                'updated_at': current_profile.updated_at
            }
            
        except Exception as e:
            logger.error(f"Error getting profile summary for {email}: {e}")
            return None


# Dependency injection
_user_profile_service: Optional[UserProfileService] = None


def get_user_profile_service() -> UserProfileService:
    """
    Get or create UserProfileService instance (singleton pattern).
    
    Returns:
        UserProfileService instance
    """
    global _user_profile_service
    if _user_profile_service is None:
        _user_profile_service = UserProfileService()
    return _user_profile_service
