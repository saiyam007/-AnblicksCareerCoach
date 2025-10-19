"""
Business logic services for authentication and user management.
Contains AuthService, UserService, and authentication dependencies.
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


logger = get_logger(__name__)

# HTTP Bearer token authentication
security = HTTPBearer()


# ============================================================================
# Authentication Service
# ============================================================================

class AuthService:
    """Authentication service for Google OAuth and token refresh."""
    
    def __init__(self, db_table=None):
        """
        Initialize auth service.
        
        Args:
            db_table: DynamoDB table (not used but kept for compatibility)
        """
        self.db_table = db_table
    
    # Removed email/password registration and login to keep only Google SSO
    
    async def google_oauth_login(self, oauth_data: GoogleOAuthRequest) -> TokenResponse:
        """
        Authenticate user with Google OAuth 2.0.
        
        Args:
            oauth_data: Google OAuth data (ID token)
            
        Returns:
            Authentication tokens and user information
            
        Raises:
            AuthenticationError: If OAuth validation fails
        """
        if not oauth_data.id_token:
            raise ValidationError(message="ID token is required for Google OAuth")
        
        # TESTING MODE: Skip Google verification if in test environment
        if settings.TESTING or settings.ENVIRONMENT == "development":
            logger.warning("TESTING MODE: Bypassing Google token verification")
            try:
                # Decode token without verification (UNSAFE - testing only)
                from jose import jwt
                decoded = jwt.decode(
                    oauth_data.id_token, 
                    key="", 
                    options={"verify_signature": False, "verify_aud": False, "verify_exp": False}
                )
                google_id = decoded.get('sub', f'test-{decoded.get("email")}')
                email = decoded.get('email')
                name = decoded.get('name', '')
                picture = decoded.get('picture')
                email_verified = decoded.get('email_verified', True)
            except Exception as e:
                logger.error(f"Failed to decode test token: {str(e)}")
                raise AuthenticationError(
                    message="Invalid token format",
                    details={"error": str(e)}
                )
        else:
            # PRODUCTION MODE: Verify with Google
            try:
                # Verify Google ID token
                idinfo = id_token.verify_oauth2_token(
                    oauth_data.id_token,
                    requests.Request(),
                    settings.GOOGLE_CLIENT_ID
                )
                
                # Verify token is for our app
                if idinfo['aud'] != settings.GOOGLE_CLIENT_ID:
                    raise AuthenticationError(message="Invalid token audience")
                
                # Extract user info from Google
                google_id = idinfo['sub']
                email = idinfo.get('email')
                name = idinfo.get('name', '')
                picture = idinfo.get('picture')
                email_verified = idinfo.get('email_verified', False)
            except ValueError as e:
                logger.error(f"Google token verification failed: {str(e)}", exc_info=True)
                raise AuthenticationError(
                    message="Invalid Google token",
                    details={"error": str(e)}
                )
            except Exception as e:
                logger.error(f"Google OAuth error: {str(e)}", exc_info=True)
                raise AuthenticationError(
                    message="Google authentication failed",
                    details={"error": str(e)}
                )
        
        # Common validation and user creation logic
        if not email:
            raise AuthenticationError(message="Email not provided by Google")
        
        # Check if user exists
        user = await User.get_by_email(email)
        
        if user:
            # Update existing user's Google info
            await user.update(
                google_id=google_id,
                profile_picture_url=picture,
                is_verified=email_verified,
                last_login_at=datetime.utcnow().isoformat()
            )
            
            logger.info(f"Existing user logged in via Google: {email}")
        else:
            # Create new user account
            # Split full name into first and last name for Users table schema
            name_parts = name.split(' ', 1) if name else []
            first_name = name_parts[0] if name_parts else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            user = User(
                email=email,
                google_id=google_id,
                full_name=name,
                first_name=first_name,
                last_name=last_name,
                profile_picture_url=picture,
                auth_provider=AuthProvider.GOOGLE.value,
                is_active=True,
                is_verified=email_verified,
                status=UserStatus.ACTIVE.value,
                journey_stage=JourneyStage.AUTHENTICATED  # Set initial stage for new user
            )
            
            await user.save()
            logger.info(f"New user created via Google OAuth in Users table: {email}")
        
        # Handle stage management for both new and existing users
        from ..services.stageServices import get_stage_service
        stage_service = get_stage_service()
        
        # For new users, they start at AUTHENTICATED stage
        # For existing users, don't change their stage (they're returning)
        if not user.journey_stage:
            # This handles existing users who don't have a stage set yet
            stage_update_result = stage_service.update_user_stage(
                email=email,
                new_stage=JourneyStage.AUTHENTICATED,
                force_update=True  # Force for existing users without stage
            )
            if stage_update_result.get("success"):
                logger.info(f"Set initial stage for existing user {email}: {JourneyStage.AUTHENTICATED}")
            else:
                logger.warning(f"Failed to set initial stage for user {email}: {stage_update_result.get('reason')}")
        
        # Generate JWT tokens using email (primary key in Users table)
        access_token = create_access_token(subject=user.email)
        refresh_token = create_refresh_token(subject=user.email)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user.to_dict())
        )
    
    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Generate new access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New authentication tokens
            
        Raises:
            AuthenticationError: If refresh token is invalid
        """
        # Verify refresh token (now contains email instead of user_id)
        user_email = verify_token(refresh_token, token_type="refresh")
        
        # Get user from database by email
        user = await User.get_by_email(user_email)
        
        if not user or not user.is_active:
            raise AuthenticationError(message="User not found or inactive")
        
        # Generate new tokens using email
        new_access_token = create_access_token(subject=user.email)
        new_refresh_token = create_refresh_token(subject=user.email)
        
        logger.info(f"Token refreshed for user: {user.email}")
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user.to_dict())
        )
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User model or None
        """
        return await User.get_by_email(email)


## Removed UserService to keep minimal profile-only API


# ============================================================================
# Authentication Dependencies
# ============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db_table = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user.
    
    JWT token now contains email (primary key in Users table) instead of user_id.
    
    Args:
        credentials: HTTP Bearer token credentials
        db_table: DynamoDB table
        
    Returns:
        Current user
        
    Raises:
        AuthenticationError: If token is invalid or user not found
    """
    try:
        # Extract token
        token = credentials.credentials
        
        # Verify token and get user email (not user_id anymore)
        user_email = verify_token(token, token_type="access")
        
        # Get user from database by email (direct lookup with composite key)
        user = await User.get_by_email(user_email)
        
        if not user:
            raise AuthenticationError(message="User not found")
        
        return user
        
    except AuthenticationError:
        raise
    except Exception as e:
        raise AuthenticationError(
            message="Could not validate credentials",
            details={"error": str(e)}
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get the current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current active user
        
    Raises:
        AuthenticationError: If user is inactive
    """
    if not current_user.is_active or current_user.status != UserStatus.ACTIVE.value:
        raise AuthenticationError(
            message="User account is inactive or suspended",
            details={"status": current_user.status}
        )
    
    return current_user


# ============================================================================
# Service Factory Dependencies
# ============================================================================

def get_auth_service(db_table = Depends(get_db)) -> AuthService:
    """
    Get authentication service instance.
    
    Args:
        db_table: DynamoDB table
        
    Returns:
        AuthService instance
    """
    return AuthService(db_table)


## Removed get_user_service dependency
