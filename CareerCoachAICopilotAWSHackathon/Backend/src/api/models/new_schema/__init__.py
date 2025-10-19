"""
New normalized data models for scalable architecture.

This package contains models for the new normalized database schema:
- User model for core user management
- UserProfile model for career profile data with versioning
- UserJourney model for journey state management
- Roadmap model for normalized roadmap data
- Assessment model for assessment & progress tracking
"""

from .user_model import NewUser
from .profile_model import UserProfile
from .journey_model import UserJourney
from .roadmap_model import Roadmap
from .assessment_model import Assessment

__all__ = [
    'NewUser',
    'UserProfile', 
    'UserJourney',
    'Roadmap',
    'Assessment'
]
