"""
Common schemas used across the application.

Provides standardized response structures for all API endpoints.
"""

from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime

# Type variable for generic response data
DataT = TypeVar('DataT')


# ============================================================================
# Standard API Response Models
# ============================================================================

class StandardResponse(BaseModel, Generic[DataT]):
    """
    Production-standard API response model.
    
    ALL successful API responses should follow this structure:
    {
        "success": true,
        "message": "Operation successful",
        "data": { ...actual response data... },
        "error": null,
        "code": 200
    }
    """
    
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Human-readable message")
    data: Optional[DataT] = Field(None, description="Response data")
    error: Optional[Any] = Field(None, description="Error details (null on success)")
    code: int = Field(..., description="HTTP status code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Item retrieved successfully",
                "data": {"item_id": 1, "name": "Laptop"},
                "error": None,
                "code": 200
            }
        }


class StandardErrorResponse(BaseModel):
    """
    Production-standard API error response model.
    
    ALL error responses should follow this structure:
    {
        "success": false,
        "message": "Error message",
        "data": null,
        "error": { ...error details... },
        "code": 400
    }
    """
    
    success: bool = Field(default=False, description="Always false for errors")
    message: str = Field(..., description="Human-readable error message")
    data: Optional[Any] = Field(default=None, description="Always null for errors")
    error: Optional[Any] = Field(None, description="Error details")
    code: int = Field(..., description="HTTP status code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Item not found",
                "data": None,
                "error": {"item_id": 0},
                "code": 404
            }
        }


# ============================================================================
# Helper Functions for Creating Responses
# ============================================================================

def success_response(
    data: Any,
    message: str = "Operation successful",
    code: int = 200
) -> dict:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        message: Success message
        code: HTTP status code
        
    Returns:
        Standardized success response dictionary
    """
    return {
        "success": True,
        "message": message,
        "data": data,
        "error": None,
        "code": code
    }


def error_response(
    message: str,
    code: int = 400,
    error_details: Optional[Any] = None
) -> dict:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        code: HTTP status code
        error_details: Additional error details
        
    Returns:
        Standardized error response dictionary
    """
    return {
        "success": False,
        "message": message,
        "data": None,
        "error": error_details,
        "code": code
    }


# ============================================================================
# Legacy Response Models (for backward compatibility)
# ============================================================================

class ResponseModel(BaseModel):
    """
    Legacy response model (deprecated - use StandardResponse instead).
    
    Kept for backward compatibility with existing endpoints.
    """
    
    status: str = Field(default="success", description="Response status")
    message: str = Field(default="Success", description="Human-readable message")
    data: Optional[Any] = Field(default=None, description="Response data")


class HealthCheck(BaseModel):
    """Health check response."""
    
    status: str = Field(default="healthy", description="Service health status")
    version: str = Field(description="API version")
    environment: str = Field(description="Environment name")
    database: str = Field(default="connected", description="Database connection status")


class ErrorResponse(BaseModel):
    """
    Legacy error response model (deprecated - use StandardErrorResponse instead).
    
    Kept for backward compatibility.
    """
    
    error: str
    message: str
    details: Optional[Any] = None
    path: Optional[str] = None
    status_code: int
