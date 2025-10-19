"""
API Helper utilities including security, logging, and general utilities.
Contains JWT token management, password hashing, and logging configuration.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from jose import JWTError, jwt
from pythonjsonlogger import jsonlogger

from .errorHandler import settings, AuthenticationError


# ============================================================================
# Logging Configuration
# ============================================================================

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that adds additional context to log records.
    """
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """Add custom fields to the log record."""
        super().add_fields(log_record, record, message_dict)
        
        # Add standard fields
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["timestamp"] = self.formatTime(record, self.datefmt)
        
        # Add environment context
        log_record["environment"] = settings.ENVIRONMENT
        log_record["app_name"] = settings.APP_NAME
        log_record["app_version"] = settings.APP_VERSION
        
        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)


def setup_logging() -> None:
    """
    Configure logging for the application.
    
    Sets up structured JSON logging for production and readable text logging
    for development. Logs are written to both console and file.
    """
    
    # Create logs directory if it doesn't exist
    log_file = Path(settings.LOG_FILE_PATH)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Determine log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Create formatters
    if settings.LOG_FORMAT.lower() == "json":
        formatter = CustomJsonFormatter(
            fmt="%(timestamp)s %(level)s %(name)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # File handler
    file_handler = logging.FileHandler(settings.LOG_FILE_PATH)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Reduce verbosity of third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__ of the module)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


## Removed password hashing utilities to keep only Google SSO


# ============================================================================
# JWT Token Management
# ============================================================================

def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: The subject of the token (usually user ID)
        expires_delta: Token expiration time delta
        additional_claims: Additional claims to include in the token
        
    Returns:
        Encoded JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "exp": expire,
        "iat": datetime.utcnow(),
        "sub": str(subject),
        "type": "access"
    }
    
    # Add additional claims if provided
    if additional_claims:
        to_encode.update(additional_claims)
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        subject: The subject of the token (usually user ID)
        expires_delta: Token expiration time delta
        
    Returns:
        Encoded JWT refresh token
    """
    if expires_delta is None:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "exp": expire,
        "iat": datetime.utcnow(),
        "sub": str(subject),
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Decoded token payload
        
    Raises:
        AuthenticationError: If token is invalid or expired
    """
    logger = get_logger(__name__)
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"Token validation failed: {str(e)}")
        raise AuthenticationError(
            message="Invalid or expired token",
            details={"error": str(e)}
        )


def verify_token(token: str, token_type: str = "access") -> str:
    """
    Verify a JWT token and extract the subject.
    
    Args:
        token: JWT token to verify
        token_type: Expected token type (access or refresh)
        
    Returns:
        Token subject (usually user ID)
        
    Raises:
        AuthenticationError: If token is invalid, expired, or wrong type
    """
    payload = decode_token(token)
    
    # Verify token type
    if payload.get("type") != token_type:
        raise AuthenticationError(
            message=f"Invalid token type. Expected {token_type}",
            details={"received_type": payload.get("type")}
        )
    
    # Extract subject
    subject: str = payload.get("sub")
    if subject is None:
        raise AuthenticationError(message="Token missing subject claim")
    
    return subject


# ============================================================================
# OAuth Utilities
# ============================================================================

## Removed unused helper functions generate_state_token and generate_api_key


# ============================================================================
# General Utility Functions
# ============================================================================

## Removed unused helper functions format_datetime and truncate_text


