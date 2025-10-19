"""
DynamoDB User model.
Contains User model and user-related operations.
"""

from datetime import datetime
from typing import Any, Optional, Dict
from enum import Enum
import uuid
from botocore.exceptions import ClientError

from ..utils.errorHandler import get_logger
from ..utils.database import get_dynamodb_table


logger = get_logger(__name__)


# ============================================================================
# Constants and Enums
# ============================================================================

from .enums import UserRole, UserStatus, AuthProvider, JourneyStage


# Maximum lengths for database fields
MAX_EMAIL_LENGTH = 255
MAX_NAME_LENGTH = 100




# ============================================================================
# User Model
# ============================================================================

class User:
    """
    User model for DynamoDB.
    
    Supports multiple authentication providers (Google OAuth, email, etc.)
    and maintains user profile information.
    """
    
    def __init__(self, **kwargs):
        """Initialize user from kwargs."""
        self.id = kwargs.get('id') or str(uuid.uuid4())
        self.email = kwargs.get('email')
        self.hashed_password = kwargs.get('hashed_password')
        
        # OAuth fields
        self.auth_provider = kwargs.get('auth_provider', AuthProvider.EMAIL.value)
        self.google_id = kwargs.get('google_id')
        self.oauth_access_token = kwargs.get('oauth_access_token')
        self.oauth_refresh_token = kwargs.get('oauth_refresh_token')
        self.oauth_token_expires_at = kwargs.get('oauth_token_expires_at')
        
        # Profile fields
        self.full_name = kwargs.get('full_name')
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.profile_picture_url = kwargs.get('profile_picture_url')
        self.phone_number = kwargs.get('phone_number')
        
        # Career profile fields (for AI features)
        self.country = kwargs.get('country')
        self.state = kwargs.get('state')
        self.userType = kwargs.get('userType')
        self.careerGoal = kwargs.get('careerGoal')
        self.fieldOfStudy = kwargs.get('fieldOfStudy')
        self.currentEducationLevel = kwargs.get('currentEducationLevel')
        self.academicInterests = kwargs.get('academicInterests')
        self.preferredStudyDestination = kwargs.get('preferredStudyDestination')
        self.lookingFor = kwargs.get('lookingFor')
        self.languagePreference = kwargs.get('languagePreference')
        self.currentJobTitle = kwargs.get('currentJobTitle')
        self.industry = kwargs.get('industry')
        self.profile_summary = kwargs.get('profile_summary')
        
        # Account status
        self.is_active = kwargs.get('is_active', True)
        self.is_verified = kwargs.get('is_verified', False)
        self.status = kwargs.get('status', UserStatus.ACTIVE.value)
        self.role = kwargs.get('role', UserRole.USER.value)
        
        # Journey stage for user flow management
        self.journey_stage = kwargs.get('journey_stage', JourneyStage.AUTHENTICATED)
        
        # Account metadata
        self.created_at = kwargs.get('created_at') or datetime.utcnow().isoformat()
        self.updated_at = kwargs.get('updated_at') or datetime.utcnow().isoformat()
        self.last_login_at = kwargs.get('last_login_at')
        self.email_verified_at = kwargs.get('email_verified_at')
        self.deleted_at = kwargs.get('deleted_at')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for DynamoDB."""
        data = {
            'email': self.email,  # Primary partition key for Users table
            'recordId': 'PROFILE#LATEST',  # Sort key for Users table (composite key)
            'id': self.id,  # Keep for JWT token generation
            'auth_provider': self.auth_provider,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'status': self.status,
            'role': self.role,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
        
        # Add optional fields if they exist
        optional_fields = [
            'hashed_password', 'google_id', 'oauth_access_token', 
            'oauth_refresh_token', 'oauth_token_expires_at',
            'full_name', 'first_name', 'last_name', 
            'profile_picture_url', 'phone_number',
            'last_login_at', 'email_verified_at', 'deleted_at',
            # Career profile fields
            'country', 'state', 'userType', 'careerGoal', 'fieldOfStudy',
            'currentEducationLevel', 'academicInterests', 'preferredStudyDestination',
            'lookingFor', 'languagePreference', 'currentJobTitle', 'industry',
            'profile_summary',
            # Journey stage
            'journey_stage'
        ]
        
        for field in optional_fields:
            value = getattr(self, field, None)
            if value is not None:
                data[field] = value
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from DynamoDB item."""
        return cls(**data)
    
    async def save(self):
        """Save user to DynamoDB Users table with composite key."""
        table = get_dynamodb_table()
        self.updated_at = datetime.utcnow().isoformat()
        
        try:
            # Users table uses composite key (email + recordId)
            # Add recordId if not present
            user_data = self.to_dict()
            if 'recordId' not in user_data:
                user_data['recordId'] = 'PROFILE#LATEST'
            
            table.put_item(Item=user_data)
            logger.info(f"User saved to Users table: {self.email}")
        except ClientError as e:
            logger.error(f"Error saving user: {str(e)}", exc_info=True)
            raise
    
    @classmethod
    async def get_by_id(cls, user_id: str) -> Optional['User']:
        """Get user by ID - uses scan to find by id regardless of key schema."""
        table = get_dynamodb_table()
        
        try:
            # First try simple get_item (for single partition key schema)
            try:
                response = table.get_item(Key={'id': user_id})
                if 'Item' in response:
                    return cls.from_dict(response['Item'])
            except ClientError as key_error:
                # If key schema doesn't match, fall back to scan
                logger.debug(f"get_item failed, falling back to scan: {str(key_error)}")
            
            # Fallback: Use scan to find the user by id
            response = table.scan(
                FilterExpression='id = :id',
                ExpressionAttributeValues={':id': user_id},
                Limit=1
            )
            
            if response['Items']:
                return cls.from_dict(response['Items'][0])
            return None
        except ClientError as e:
            logger.error(f"Error getting user by ID: {str(e)}", exc_info=True)
            return None
    
    @classmethod
    async def get_by_email(cls, email: str) -> Optional['User']:
        """Get user by email using composite key (email + recordId)."""
        table = get_dynamodb_table()
        
        try:
            # Users table uses composite key: email (partition) + recordId (sort)
            # Always use "PROFILE#LATEST" as recordId for current profile
            response = table.get_item(
                Key={
                    'email': email,
                    'recordId': 'PROFILE#LATEST'
                }
            )
            
            if 'Item' in response:
                return cls.from_dict(response['Item'])
            
            logger.debug(f"User not found with email: {email}")
            return None
            
        except ClientError as e:
            logger.error(f"Error getting user by email: {str(e)}", exc_info=True)
            return None
    
    @classmethod
    async def get_by_google_id(cls, google_id: str) -> Optional['User']:
        """Get user by Google ID - tries GSI first, falls back to scan."""
        table = get_dynamodb_table()
        
        try:
            # First try to use the google-id-index GSI
            try:
                response = table.query(
                    IndexName='google-id-index',
                    KeyConditionExpression='google_id = :google_id',
                    ExpressionAttributeValues={':google_id': google_id}
                )
                
                if response['Items']:
                    return cls.from_dict(response['Items'][0])
                return None
            except ClientError as index_error:
                # If index doesn't exist, fall back to scan
                if index_error.response['Error']['Code'] == 'ValidationException':
                    logger.debug("google-id-index not found, falling back to scan")
                else:
                    raise
            
            # Fallback: Use scan to find the user by google_id
            # Note: This is less efficient but works without GSI
            response = table.scan(
                FilterExpression='google_id = :google_id',
                ExpressionAttributeValues={':google_id': google_id},
                Limit=1
            )
            
            if response['Items']:
                return cls.from_dict(response['Items'][0])
            return None
        except ClientError as e:
            logger.error(f"Error getting user by Google ID: {str(e)}", exc_info=True)
            return None
    
    async def update(self, **kwargs):
        """Update user fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow().isoformat()
        await self.save()
    
    async def delete(self):
        """Soft delete user."""
        self.is_active = False
        self.status = UserStatus.DELETED.value
        self.deleted_at = datetime.utcnow().isoformat()
        await self.save()
    
    @property
    def is_oauth_user(self) -> bool:
        """Check if user authenticated via OAuth."""
        return self.auth_provider != AuthProvider.EMAIL.value
    
    @property
    def display_name(self) -> str:
        """Get user's display name."""
        if self.full_name:
            return self.full_name
        elif self.first_name:
            return f"{self.first_name} {self.last_name or ''}".strip()
        return self.email.split('@')[0] if self.email else "User"
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


