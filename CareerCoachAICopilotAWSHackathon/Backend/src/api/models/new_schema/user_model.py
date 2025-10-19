"""
New User model for normalized users table.

Handles core user management with clean separation from profile data.
"""

from datetime import datetime
from typing import Any, Optional, Dict
import uuid
from enum import Enum

from ...utils.errorHandler import get_logger

logger = get_logger(__name__)


class AuthProvider(str, Enum):
    """Authentication provider enumeration."""
    GOOGLE = "google"
    EMAIL = "email"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"


class UserStatus(str, Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class UserRole(str, Enum):
    """User role enumeration."""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"
    SUPPORT = "support"


class NewUser:
    """
    New User model for normalized users table.
    
    Handles core user management:
    - Authentication data
    - Basic profile info
    - Account status
    - No career-specific data (moved to UserProfile)
    """
    
    def __init__(self, **kwargs):
        """Initialize user from kwargs."""
        
        # Core identifiers
        self.email = kwargs.get('email')  # Primary key
        self.id = kwargs.get('id') or str(uuid.uuid4())  # Unique identifier
        
        # Authentication
        self.auth_provider = kwargs.get('auth_provider', AuthProvider.EMAIL.value)
        self.google_id = kwargs.get('google_id')
        self.oauth_access_token = kwargs.get('oauth_access_token')
        self.oauth_refresh_token = kwargs.get('oauth_refresh_token')
        self.oauth_token_expires_at = kwargs.get('oauth_token_expires_at')
        
        # Basic profile (non-career specific)
        self.full_name = kwargs.get('full_name')
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.profile_picture_url = kwargs.get('profile_picture_url')
        self.phone_number = kwargs.get('phone_number')
        
        # Account status
        self.is_active = kwargs.get('is_active', True)
        self.is_verified = kwargs.get('is_verified', False)
        self.status = kwargs.get('status', UserStatus.ACTIVE.value)
        self.role = kwargs.get('role', UserRole.USER.value)
        
        # Timestamps
        self.created_at = kwargs.get('created_at') or datetime.utcnow().isoformat()
        self.updated_at = kwargs.get('updated_at') or datetime.utcnow().isoformat()
        self.last_login_at = kwargs.get('last_login_at')
        self.email_verified_at = kwargs.get('email_verified_at')
        self.deleted_at = kwargs.get('deleted_at')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for DynamoDB."""
        
        data = {
            'email': self.email,  # Partition key
            'id': self.id,
            'auth_provider': self.auth_provider,
            'google_id': self.google_id,
            'oauth_access_token': self.oauth_access_token,
            'oauth_refresh_token': self.oauth_refresh_token,
            'oauth_token_expires_at': self.oauth_token_expires_at,
            'full_name': self.full_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'profile_picture_url': self.profile_picture_url,
            'phone_number': self.phone_number,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'status': self.status,
            'role': self.role,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'last_login_at': self.last_login_at,
            'email_verified_at': self.email_verified_at,
            'deleted_at': self.deleted_at
        }
        
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    def verify_email(self):
        """Mark email as verified."""
        self.is_verified = True
        self.email_verified_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    def deactivate(self):
        """Deactivate user account."""
        self.is_active = False
        self.status = UserStatus.INACTIVE.value
        self.updated_at = datetime.utcnow().isoformat()
    
    def suspend(self):
        """Suspend user account."""
        self.is_active = False
        self.status = UserStatus.SUSPENDED.value
        self.updated_at = datetime.utcnow().isoformat()
    
    def soft_delete(self):
        """Soft delete user account."""
        self.is_active = False
        self.status = UserStatus.DELETED.value
        self.deleted_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NewUser':
        """Create user from DynamoDB dictionary."""
        return cls(**data)
    
    def __repr__(self) -> str:
        return f"NewUser(email='{self.email}', auth_provider='{self.auth_provider}', status='{self.status}')"
