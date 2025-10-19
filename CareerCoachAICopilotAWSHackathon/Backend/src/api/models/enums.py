"""
Shared enum definitions for user-related concepts.
"""

from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class AuthProvider(str, Enum):
    GOOGLE = "google"
    EMAIL = "email"
    FACEBOOK = "facebook"
    APPLE = "apple"


class JourneyStage(str, Enum):
    """User journey stages for frontend redirection management"""
    AUTHENTICATED = "AUTHENTICATED"  # First time login - needs basic registration
    BASIC_REGISTERED = "BASIC_REGISTERED"  # Basic details saved - needs AI profile completion
    PROFILE_COMPLETED = "PROFILE_COMPLETED"  # AI profile done - needs career paths generation
    CAREER_PATHS_GENERATED = "CAREER_PATHS_GENERATED"  # Paths available - user needs to select one
    CAREER_PATH_SELECTED = "CAREER_PATH_SELECTED"  # Path chosen - needs roadmap generation
    ROADMAP_GENERATED = "ROADMAP_GENERATED"  # Roadmap ready - user can start journey
    ROADMAP_ACTIVE = "ROADMAP_ACTIVE"  # Journey in progress
    JOURNEY_COMPLETED = "JOURNEY_COMPLETED"  # Full journey completed
    JOURNEY_PAUSED = "JOURNEY_PAUSED"  # User paused but can resume


