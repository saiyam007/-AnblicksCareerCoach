"""
New User Services using the normalized schema.

This module provides updated authentication and user management services
that use the new normalized database schema while maintaining backward
compatibility with existing API responses.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.oauth2 import id_token
from google.auth.transport import requests

from ..models.userModel import User
from ..models.enums import UserStatus, AuthProvider, JourneyStage
from ..utils.database import get_db
from ..schemas import (
    TokenResponse,
    GoogleOAuthRequest,
    UserResponse,
    UserUpdate,
)
from ..utils.errorHandler import (
    settings,
    get_logger,
    AuthenticationError,
    NotFoundError,
    ValidationError,
)
from ..utils.apiHelper import (
    create_access_token,
    create_refresh_token,
    verify_token,
)

# Import new schema services
from .new_schema.user_service import get_new_user_service
from .new_schema.profile_service import get_user_profile_service
from .new_schema.journey_service import get_user_journey_service
from .transformation_service import get_transformation_service

logger = get_logger(__name__)

# HTTP Bearer token authentication
security = HTTPBearer()


# ============================================================================
# New Authentication Service
# ============================================================================

class NewAuthService:
    """Authentication service using the new normalized schema."""
    
    def __init__(self):
        """Initialize with new schema services."""
        from .new_schema.user_service import NewUserService as NewUserServiceClass
        self.user_service = NewUserServiceClass()
        self.profile_service = get_user_profile_service()
        self.journey_service = get_user_journey_service()
        self.transformation_service = get_transformation_service()
    
    async def authenticate_google_user(self, google_token: str) -> TokenResponse:
        """
        Authenticate user with Google ID token and return JWT tokens.
        
        Args:
            google_token: Google ID token from frontend
            
        Returns:
            TokenResponse: Access and refresh tokens
            
        Raises:
            AuthenticationError: If token validation fails
        """
        try:
            # TESTING MODE: Skip Google verification if in test environment
            if settings.TESTING or settings.ENVIRONMENT == "development":
                logger.warning("TESTING MODE: Bypassing Google token verification")
                try:
                    # Decode token without verification (UNSAFE - testing only)
                    from jose import jwt
                    decoded = jwt.decode(
                        google_token, 
                        key="", 
                        options={"verify_signature": False, "verify_aud": False, "verify_exp": False}
                    )
                    idinfo = {
                        'sub': decoded.get('sub', f'test-{decoded.get("email")}'),
                        'email': decoded.get('email'),
                        'name': decoded.get('name', ''),
                        'given_name': decoded.get('given_name', ''),
                        'family_name': decoded.get('family_name', ''),
                        'picture': decoded.get('picture', ''),
                        'email_verified': decoded.get('email_verified', True)
                    }
                except Exception as e:
                    # If decoding fails, create mock data for testing
                    idinfo = {
                        'sub': 'test-user',
                        'email': 'test@example.com',
                        'name': 'Test User',
                        'given_name': 'Test',
                        'family_name': 'User',
                        'picture': '',
                        'email_verified': True
                    }
            else:
                # Verify Google token
                idinfo = id_token.verify_oauth2_token(
                    google_token, 
                    requests.Request(), 
                    settings.GOOGLE_CLIENT_ID
                )
            
            email = idinfo.get('email')
            if not email:
                raise AuthenticationError("Email not found in Google token")
            
            logger.info(f"Google token verified for user: {email}")
            
            # Check if user exists in new schema
            user = self.user_service.get_user(email)
            
            if not user:
                # Create new user in new schema
                user_data = {
                    'email': email,
                    'full_name': idinfo.get('name'),
                    'first_name': idinfo.get('given_name'),
                    'last_name': idinfo.get('family_name'),
                    'auth_provider': AuthProvider.GOOGLE.value,
                    'profile_picture_url': idinfo.get('picture'),
                    'is_verified': idinfo.get('email_verified', False),
                    'status': UserStatus.ACTIVE.value,
                    'role': 'user'
                }
                
                user = self.user_service.create_user(user_data)
                
                # Create initial journey
                self.journey_service.create_journey(email)
                
                logger.info(f"Created new user in new schema: {email}")
            else:
                # Update last login
                self.user_service.update_last_login(email)
                logger.info(f"Existing user logged in via Google: {email}")
            
            # Create JWT tokens
            access_token = create_access_token(subject=email)
            refresh_token = create_refresh_token(subject=email)
            
            # Transform user data for response
            user_response = self.transformation_service.transform_user_to_legacy_format(user.to_dict())
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=user_response
            )
            
        except ValueError as e:
            logger.error(f"Google token validation failed: {e}")
            raise AuthenticationError("Invalid Google token")
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise AuthenticationError(f"Authentication failed: {str(e)}")
    
    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            TokenResponse: New access and refresh tokens
            
        Raises:
            AuthenticationError: If refresh token is invalid
        """
        try:
            # Verify refresh token
            payload = verify_token(refresh_token)
            email = payload.get("sub")
            
            if not email:
                raise AuthenticationError("Invalid refresh token")
            
            # Check if user exists in new schema
            user = self.user_service.get_user(email)
            if not user:
                raise AuthenticationError("User not found")
            
            # Create new tokens
            access_token = create_access_token(subject=email)
            new_refresh_token = create_refresh_token(subject=email)
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise AuthenticationError("Invalid refresh token")


# ============================================================================
# New User Service
# ============================================================================

class NewUserService:
    """User service using the new normalized schema."""
    
    def __init__(self):
        """Initialize with new schema services."""
        from .new_schema.user_service import NewUserService as NewUserServiceClass
        self.user_service = NewUserServiceClass()
        self.profile_service = get_user_profile_service()
        self.journey_service = get_user_journey_service()
        self.transformation_service = get_transformation_service()
    
    def get_user(self, email: str):
        """Get user from new schema service."""
        return self.user_service.get_user(email)
    
    def create_or_update_user(self, user_data: dict):
        """Create or update user using new schema service."""
        return self.user_service.create_user(user_data)
    
    def create_or_update_profile(self, profile_data: dict):
        """Create or update profile using new schema service."""
        email = profile_data.get('email')
        if not email:
            raise ValueError("Email is required for profile creation")
        return self.profile_service.create_profile(email, profile_data)
    
    def get_user_profile(self, email: str) -> Optional[User]:
        """
        Get user profile using new schema and transform to legacy User model.
        
        Args:
            email: User email address
            
        Returns:
            User: Legacy user model for API compatibility
        """
        try:
            # Get user from new schema
            new_user = self.user_service.get_user(email)
            if not new_user:
                return None
            
            # Get current profile
            profile = self.profile_service.get_current_profile(email)
            
            # Get current journey
            journey = self.journey_service.get_active_journey(email)
            
            # Transform to legacy format (including profile data)
            if profile:
                legacy_user_data = self.transformation_service.transform_profile_to_legacy_format(
                    new_user.to_dict(), profile.to_dict()
                )
            else:
                # Fallback if no profile exists
                combined_user_data = {
                    **new_user.to_dict(),
                    'profile': None,
                    'journey': journey.to_dict() if journey else None
                }
                legacy_user_data = self.transformation_service.transform_user_to_legacy_format(
                    combined_user_data
                )
            
            # Create legacy User object
            return User(**legacy_user_data)
            
        except Exception as e:
            logger.error(f"Error getting user profile for {email}: {e}")
            return None
    
    def update_user_profile(self, email: str, user_data: dict) -> Optional[User]:
        """
        Update user profile using new schema.
        
        Args:
            email: User email address
            user_data: Updated user data
            
        Returns:
            User: Updated legacy user model
        """
        try:
            # Update user in new schema
            updated_user = self.user_service.update_user(email, user_data)
            if not updated_user:
                return None
            
            # Get updated profile and journey
            profile = self.profile_service.get_current_profile(email)
            journey = self.journey_service.get_active_journey(email)
            
            # Transform to legacy format (including profile data)
            if profile:
                legacy_user_data = self.transformation_service.transform_profile_to_legacy_format(
                    updated_user.to_dict(), profile.to_dict()
                )
            else:
                # Fallback if no profile exists
                combined_user_data = {
                    **updated_user.to_dict(),
                    'profile': None,
                    'journey': journey.to_dict() if journey else None
                }
                legacy_user_data = self.transformation_service.transform_user_to_legacy_format(
                    combined_user_data
                )
            
            return User(**legacy_user_data)
            
        except Exception as e:
            logger.error(f"Error updating user profile for {email}: {e}")
            return None
    
    def delete_user(self, email: str) -> bool:
        """
        Delete user from new schema.
        
        Args:
            email: User email address
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            return self.user_service.delete_user(email)
        except Exception as e:
            logger.error(f"Error deleting user {email}: {e}")
            return False


# ============================================================================
# Authentication Dependencies
# ============================================================================

def get_new_auth_service() -> NewAuthService:
    """Get new authentication service instance."""
    return NewAuthService()


def get_new_user_service() -> NewUserService:
    """Get new user service instance."""
    return NewUserService()


async def get_current_active_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get current active user from JWT token using new schema.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        User: Current authenticated user
        
    Raises:
        AuthenticationError: If token is invalid or user not found
    """
    try:
        # Verify JWT token
        token = credentials.credentials
        email = verify_token(token)
        
        if not email:
            raise AuthenticationError("Invalid token")
        
        # Use only new schema authentication
        user_service = get_new_user_service()
        user = user_service.get_user(email)
        
        if not user:
            raise AuthenticationError("User not found")
        
        if user.status != UserStatus.ACTIVE.value:
            raise AuthenticationError("User account is not active")
        
        # Get profile data from new schema
        profile_service = get_user_profile_service()
        profile = profile_service.get_current_profile(email)
        
        # Create user data with profile information
        user_data = {
            'email': user.email,
            'full_name': user.full_name,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'status': user.status,
            'created_at': user.created_at,
            'updated_at': user.updated_at,
            'is_active': True  # Legacy field for compatibility
        }
        
        # Add profile data if available
        if profile:
            user_data.update({
                'careerGoal': profile.career_goal,
                'country': profile.country,
                'state': profile.state,
                'userType': profile.user_type,
                'lookingFor': profile.looking_for,
                'languagePreference': profile.language_preference,
                'currentEducationLevel': profile.current_education_level,
                'fieldOfStudy': profile.field_of_study,
                'academicInterests': profile.academic_interests,
                'preferredStudyDestination': profile.preferred_study_destination,
                'currentJobTitle': profile.current_job_title,
                'industry': profile.industry,
                'profile_summary': profile.profile_summary
            })
        
        # Create User object from data
        from ..models.userModel import User
        return User(**user_data)
        
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise AuthenticationError("Authentication failed")


# ============================================================================
# Service Factory Dependencies (for backward compatibility)
# ============================================================================

def get_auth_service() -> NewAuthService:
    """Get authentication service instance (new schema)."""
    return NewAuthService()


def get_user_service() -> NewUserService:
    """Get user service instance (new schema)."""
    return NewUserService()
