"""
Authentication endpoints for user registration, login, and OAuth.
"""

from fastapi import APIRouter, Depends, status
## Removed DB dependency for health to avoid blocking
from ..services.new_userServices import NewAuthService, get_new_auth_service
from ..schemas import (
    TokenResponse,
    GoogleOAuthRequest,
    RefreshTokenRequest,
)
from ..utils.apiHelper import get_logger
from ..utils.errorHandler import settings


logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Access Token",
    description="Get new access token using refresh token"
)
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    auth_service: NewAuthService = Depends(get_new_auth_service)
) -> TokenResponse:
    """
    Refresh access token using refresh token.
    
    When the access token expires (30 minutes), the frontend can use this
    endpoint to get a new access token without requiring the user to
    sign in with Google again.
    
    Args:
        refresh_data: Refresh token request containing the refresh token
        auth_service: Authentication service
        
    Returns:
        TokenResponse: New access token, refresh token, and user information
        
    Raises:
        AuthenticationError: If refresh token is invalid or expired
    """
    tokens = await auth_service.refresh_tokens(refresh_data.refresh_token)
    
    logger.info("Access token refreshed successfully")
    
    return tokens


@router.post(
    "/google",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Google Sign-In",
    description="Authenticate user with Google ID token"
)
async def google_signin(
    oauth_data: GoogleOAuthRequest,
    auth_service: NewAuthService = Depends(get_new_auth_service)
) -> TokenResponse:
    """
    Authenticate user with Google Sign-In.
    
    The frontend uses Google's JavaScript library to get an ID token,
    then sends it to this endpoint for verification and authentication.
    
    Args:
        oauth_data: Google OAuth data containing ID token
        auth_service: Authentication service
        
    Returns:
        TokenResponse: Authentication tokens and user information
        
    Raises:
        AuthenticationError: If Google authentication fails
    """
    tokens = await auth_service.authenticate_google_user(oauth_data.id_token)
    
    logger.info("User logged in via Google Sign-In")
    
    return tokens


## Removed email/password login, registration, and logout to keep only Google SSO


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check the health status of the API and its dependencies"
)
async def health_check():
    """
    Health check endpoint.
    
    Returns service health status including:
    - API version
    - Environment
    - Database connection status
    
    Returns:
        HealthCheck: Service health information
    """
    # Check database connection
    from ..utils.database import check_db_health
    
    try:
        db_health = await check_db_health()
        db_status = db_health.get('status', 'unknown')
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
    }


