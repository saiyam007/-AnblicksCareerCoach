"""
Error handling, exceptions, and application configuration.
Contains custom exceptions, exception handlers, and Pydantic settings.
"""

from typing import List, Optional, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# ============================================================================
# Logging Helper
# ============================================================================

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__ of the module)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

logger = get_logger(__name__)

# 📁 Load .env file from Backend root (not src directory)
env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    logger.info(f"[INFO] Loaded .env from: {env_path}")
else:
    logger.info(f"[WARNING] .env file not found at {env_path}")


# ============================================================================
# Application Settings
# ============================================================================

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings are validated using Pydantic and can be overridden
    via environment variables or .env file.
    """
    
    # Application Settings
    APP_NAME: str = "Backend API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=True, description="Debug mode")
    API_V1_PREFIX: str = "/v1"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # Security
    SECRET_KEY: str = Field(
        default="CHANGE-THIS-IN-PRODUCTION-USE-MINIMUM-32-CHARACTERS",
        description="Secret key for JWT token generation"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS Settings
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str = Field(default="", description="AWS Access Key ID")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", description="AWS Secret Access Key")
    AWS_REGION: str = Field(default="us-east-1", description="AWS Region")
    
    # DynamoDB Configuration
    DYNAMODB_TABLE_NAME: str = Field(default="Users", description="DynamoDB table name for user profiles")
    DYNAMODB_ENDPOINT_URL: Optional[str] = Field(default=None, description="DynamoDB endpoint URL (for local)")
    DYNAMODB_REGION: str = Field(default="us-east-1", description="DynamoDB region")
    
    # AWS Bedrock (AI) Configuration
    BEDROCK_MODEL_ID: str = Field(default="arn:aws:bedrock:us-east-2:*:inference-profile/global.anthropic.claude-sonnet-4-5-20250929-v1:0", description="Bedrock model ID for AI")
    BEDROCK_REGION: str = Field(default="us-east-2", description="Bedrock region")
    DRY_RUN: bool = Field(default=False, description="DRY_RUN mode for testing without AWS calls")
    BEDROCK_DETAILED_ROADMAP_AGENT_ID: str = Field(default="", description="Bedrock Agent ID for detailed roadmap generation")
    BEDROCK_DETAILED_ROADMAP_AGENT_ALIAS_ID: str = Field(default="", description="Bedrock Agent Alias ID for detailed roadmap generation")
    BEDROCK_ASSESSMENT_AGENT_ID: str = Field(default="", description="Bedrock Agent ID for assessment generation and evaluation")
    BEDROCK_ASSESSMENT_AGENT_ALIAS_ID: str = Field(default="", description="Bedrock Agent Alias ID for assessment generation and evaluation")
    
    # Google OAuth 2.0
    GOOGLE_CLIENT_ID: str = Field(default="", description="Google OAuth Client ID")
    GOOGLE_CLIENT_SECRET: str = Field(default="", description="Google OAuth Client Secret")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format: json or text")
    LOG_FILE_PATH: str = Field(default="logs/app.log", description="Log file path")
    
    # Testing
    TESTING: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def aws_configured(self) -> bool:
        """Check if AWS credentials are configured."""
        return bool(self.AWS_ACCESS_KEY_ID and self.AWS_SECRET_ACCESS_KEY)
    
    @property
    def is_lambda(self) -> bool:
        """Check if running in AWS Lambda."""
        return bool(os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
    
    @property
    def is_local(self) -> bool:
        """Check if running locally (not in Lambda)."""
        return not self.is_lambda
    
    @property
    def cors_origins_for_environment(self) -> List[str]:
        """Get CORS origins based on environment."""
        if self.ENVIRONMENT == "production":
            # Production: Only allow your production domain
            return ["https://careercoach.anblicks.com"]
        elif self.ENVIRONMENT == "development":
            # Development: Allow dev domain + localhost for testing
            return ["https://your-dev-domain.com", "http://localhost:3000", "http://localhost:5173","https://careercoach.anblicks.com"]
        else:  # local or default
            # Local: Only allow localhost
            return ["http://localhost:3000", "http://localhost:5173","https://careercoach.anblicks.com"]


# Global settings instance
settings = Settings()

# ============================================================================
# Custom Exception Classes
# ============================================================================

class BaseAppException(Exception):
    """
    Base exception class for all application exceptions.
    
    All custom exceptions should inherit from this class for consistent
    error handling and logging.
    """
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class AuthenticationError(BaseAppException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class AuthorizationError(BaseAppException):
    """Raised when user doesn't have permission to access a resource."""
    
    def __init__(self, message: str = "Access forbidden", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class NotFoundError(BaseAppException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class ValidationError(BaseAppException):
    """Raised when data validation fails."""
    
    def __init__(self, message: str = "Validation error", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class ConflictError(BaseAppException):
    """Raised when there's a conflict with existing data."""
    
    def __init__(self, message: str = "Resource conflict", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class RateLimitError(BaseAppException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


class ExternalServiceError(BaseAppException):
    """Raised when an external service (AWS, Google, etc.) fails."""
    
    def __init__(
        self,
        message: str = "External service error",
        details: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details
        )


class DatabaseError(BaseAppException):
    """Raised when a database operation fails."""
    
    def __init__(self, message: str = "Database error", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


# ============================================================================
# Exception Handlers
# ============================================================================

async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """
    Handler for all custom application exceptions.
    
    Args:
        request: The incoming request
        exc: The raised exception
        
    Returns:
        JSON response with error details
    """
    logger.error(
        f"Application error: {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "details": exc.details
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "data": None,
            "error": {
                "type": exc.__class__.__name__,
                "details": exc.details,
                "path": request.url.path
            },
            "code": exc.status_code
        }
    )


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for FastAPI HTTPException.
    
    Args:
        request: The incoming request
        exc: The raised HTTPException
        
    Returns:
        JSON response with error details
    """
    from fastapi import HTTPException
    
    if isinstance(exc, HTTPException):
        logger.warning(
            f"HTTP exception: {exc.detail}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": exc.status_code
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail,
                "data": None,
                "error": {
                    "type": "HTTPException",
                    "path": request.url.path
                },
                "code": exc.status_code
            }
        )
    
    return await general_exception_handler(request, exc)


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handler for Pydantic validation errors.
    
    Args:
        request: The incoming request
        exc: The validation error
        
    Returns:
        JSON response with validation error details
    """
    logger.warning(
        "Validation error",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors()
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Request validation failed",
            "data": None,
            "error": {
                "type": "ValidationError",
                "details": exc.errors(),
                "path": request.url.path
            },
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for all unhandled exceptions.
    
    Args:
        request: The incoming request
        exc: The raised exception
        
    Returns:
        JSON response with error details
    """
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected error occurred",
            "data": None,
            "error": {
                "type": "InternalServerError",
                "details": str(exc),
                "path": request.url.path
            },
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR
        }
    )


