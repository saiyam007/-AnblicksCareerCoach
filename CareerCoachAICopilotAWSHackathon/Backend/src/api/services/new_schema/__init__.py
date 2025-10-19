"""
New normalized service layer for scalable architecture.

This package contains services for the new normalized database schema:
- NewUserService for core user management
- UserProfileService for career profile data with versioning
- UserJourneyService for journey state management
- RoadmapService for normalized roadmap data
- AssessmentService for assessment & progress tracking
"""

from .user_service import NewUserService
from .profile_service import UserProfileService
from .journey_service import UserJourneyService
from .roadmap_service import NewRoadmapService
from .assessment_service import NewAssessmentService

__all__ = [
    'NewUserService',
    'UserProfileService',
    'UserJourneyService',
    'NewRoadmapService',
    'NewAssessmentService'
]
