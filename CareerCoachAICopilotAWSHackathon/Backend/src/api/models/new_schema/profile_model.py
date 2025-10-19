"""
User Profile model for normalized user_profiles table.

Handles career profile data with versioning support.
"""

from datetime import datetime
from typing import Any, Optional, Dict, List
import uuid
from enum import Enum

from ...utils.errorHandler import get_logger

logger = get_logger(__name__)


class UserType(str, Enum):
    """User type enumeration."""
    STUDENT = "Student"
    PROFESSIONAL = "Professional"
    CAREER_CHANGER = "Career Changer"
    FREELANCER = "Freelancer"
    ENTREPRENEUR = "Entrepreneur"


class EducationLevel(str, Enum):
    """Education level enumeration."""
    HIGH_SCHOOL = "High School"
    BACHELOR = "Bachelor degree"
    MASTER = "Master degree"
    DOCTORATE = "Doctorate"
    CERTIFICATION = "Certification"
    OTHER = "Other"


class UserProfile:
    """
    User Profile model for normalized user_profiles table.
    
    Handles career profile data with versioning:
    - Career goals and preferences
    - Educational background
    - Professional experience
    - AI-generated summaries
    - Version history for tracking changes
    """
    
    def __init__(self, **kwargs):
        """Initialize user profile from kwargs."""
        
        # Core identifiers
        self.email = kwargs.get('email')  # Partition key
        self.profile_version = kwargs.get('profile_version') or f"v{int(datetime.utcnow().timestamp())}"  # Sort key
        self.is_current = kwargs.get('is_current', 'true')  # GSI key (string for DynamoDB)
        
        # Career information
        self.user_type = kwargs.get('user_type')  # Student, Professional, etc.
        self.career_goal = kwargs.get('career_goal')
        self.looking_for = kwargs.get('looking_for')  # Skill Development, Job Change, etc.
        self.preferred_study_destination = kwargs.get('preferred_study_destination')
        
        # Educational background
        self.current_education_level = kwargs.get('current_education_level')
        self.field_of_study = kwargs.get('field_of_study')
        self.academic_interests = kwargs.get('academic_interests')
        
        # Professional background
        self.current_job_title = kwargs.get('current_job_title')
        self.industry = kwargs.get('industry')
        self.years_of_experience = kwargs.get('years_of_experience')
        self.current_company = kwargs.get('current_company')
        
        # Preferences
        self.language_preference = kwargs.get('language_preference', 'English')
        self.country = kwargs.get('country')
        self.state = kwargs.get('state')
        self.city = kwargs.get('city')
        
        # AI-generated content
        self.profile_summary = kwargs.get('profile_summary')
        self.ai_insights = kwargs.get('ai_insights', {})
        self.skill_gaps = kwargs.get('skill_gaps', [])
        self.recommendations = kwargs.get('recommendations', [])
        
        # Metadata
        self.source = kwargs.get('source', 'manual')  # manual, ai_completed, imported
        self.tags = kwargs.get('tags', [])  # For categorization
        self.is_complete = kwargs.get('is_complete', False)
        
        # Timestamps
        self.created_at = kwargs.get('created_at') or datetime.utcnow().isoformat()
        self.updated_at = kwargs.get('updated_at') or datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for DynamoDB."""
        
        data = {
            'email': self.email,  # Partition key
            'profile_version': self.profile_version,  # Sort key
            'is_current': self.is_current,  # GSI key
            'user_type': self.user_type,
            'career_goal': self.career_goal,
            'looking_for': self.looking_for,
            'preferred_study_destination': self.preferred_study_destination,
            'current_education_level': self.current_education_level,
            'field_of_study': self.field_of_study,
            'academic_interests': self.academic_interests,
            'current_job_title': self.current_job_title,
            'industry': self.industry,
            'years_of_experience': self.years_of_experience,
            'current_company': self.current_company,
            'language_preference': self.language_preference,
            'country': self.country,
            'state': self.state,
            'city': self.city,
            'profile_summary': self.profile_summary,
            'ai_insights': self.ai_insights,
            'skill_gaps': self.skill_gaps,
            'recommendations': self.recommendations,
            'source': self.source,
            'tags': self.tags,
            'is_complete': self.is_complete,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}
    
    def create_new_version(self, updated_fields: Dict[str, Any]) -> 'UserProfile':
        """Create a new version of the profile with updated fields."""
        
        # Mark current version as not current
        self.is_current = 'false'
        
        # Create new version
        new_version_data = self.to_dict()
        new_version_data.update(updated_fields)
        new_version_data['profile_version'] = f"v{int(datetime.utcnow().timestamp())}"
        new_version_data['is_current'] = 'true'
        new_version_data['created_at'] = datetime.utcnow().isoformat()
        new_version_data['updated_at'] = datetime.utcnow().isoformat()
        
        return UserProfile.from_dict(new_version_data)
    
    def mark_as_complete(self):
        """Mark profile as complete."""
        self.is_complete = True
        self.updated_at = datetime.utcnow().isoformat()
    
    def add_ai_insight(self, insight_type: str, insight_data: Any):
        """Add AI-generated insight."""
        if not self.ai_insights:
            self.ai_insights = {}
        
        self.ai_insights[insight_type] = insight_data
        self.updated_at = datetime.utcnow().isoformat()
    
    def add_skill_gap(self, skill_gap: str):
        """Add identified skill gap."""
        if skill_gap not in self.skill_gaps:
            self.skill_gaps.append(skill_gap)
            self.updated_at = datetime.utcnow().isoformat()
    
    def add_recommendation(self, recommendation: Dict[str, Any]):
        """Add AI recommendation."""
        self.recommendations.append(recommendation)
        self.updated_at = datetime.utcnow().isoformat()
    
    def add_tag(self, tag: str):
        """Add categorization tag."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow().isoformat()
    
    def get_career_context(self) -> Dict[str, Any]:
        """Get career context for AI processing."""
        return {
            'user_type': self.user_type,
            'career_goal': self.career_goal,
            'current_education_level': self.current_education_level,
            'field_of_study': self.field_of_study,
            'academic_interests': self.academic_interests,
            'current_job_title': self.current_job_title,
            'industry': self.industry,
            'years_of_experience': self.years_of_experience,
            'looking_for': self.looking_for
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create profile from DynamoDB dictionary."""
        return cls(**data)
    
    def __repr__(self) -> str:
        return f"UserProfile(email='{self.email}', version='{self.profile_version}', current={self.is_current})"
