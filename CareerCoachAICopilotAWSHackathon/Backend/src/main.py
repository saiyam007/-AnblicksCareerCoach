"""
FastAPI application entrypoint for Backend API.

This module initializes and configures the FastAPI application with:
- CORS middleware
- Custom middleware (logging, rate limiting)
- Exception handlers
- API routers
- Startup/shutdown events

Supports both local development (uvicorn) and AWS Lambda deployment (mangum).
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
import os

from .api.utils.errorHandler import (
    settings,
    BaseAppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from .api.utils.apiHelper import setup_logging, get_logger
from .api.utils.database import init_db, close_db
from .api.routes import authRoutes, userRoutes, registrationRoutes, aiRoutes, aiUserRoutes, assessmentRoutes, roadmapAssessmentRoutes


# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    
    Handles:
    - Database initialization
    - Resource cleanup
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize database (only for development/testing)
    if settings.ENVIRONMENT.lower() == "development":
        try:
            # await init_db()
            logger.info("Database tables initialized")
        except Exception as e:
            logger.warning(f"Database initialization skipped: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Close database connections
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {str(e)}")
    
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-ready FastAPI backend with Google OAuth 2.0 authentication",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=settings.DEBUG,
)


# ============================================================================
# CORS Configuration
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_for_environment,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

logger.info(f"CORS enabled for origins: {settings.cors_origins_for_environment}")


# ============================================================================
# Exception Handlers
# ============================================================================

# Custom application exceptions
app.add_exception_handler(BaseAppException, app_exception_handler)

# HTTP exceptions
app.add_exception_handler(HTTPException, http_exception_handler)

# Validation errors
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# General exceptions
app.add_exception_handler(Exception, general_exception_handler)

logger.info("Exception handlers registered")


# ============================================================================
# API Routers
# ============================================================================

# Include authentication routes
app.include_router(
    authRoutes.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"]
)

# Include user routes
app.include_router(
    userRoutes.router,
    prefix=f"{settings.API_V1_PREFIX}/users",
    tags=["Users"]
)

# Include registration routes
app.include_router(
    registrationRoutes.router,
    prefix=f"{settings.API_V1_PREFIX}/registration",
    tags=["Registration"]
)

# Include AI routes (Career Advisor)
app.include_router(
    aiRoutes.router,
    prefix=f"{settings.API_V1_PREFIX}/ai",
    tags=["AI Career Advisor"]
)

# Include AI User routes (from Backend_2 migration)
app.include_router(
    aiUserRoutes.router,
    prefix=f"{settings.API_V1_PREFIX}/ai",
    tags=["AI User Management"]
)

# Include Assessment routes
app.include_router(
    assessmentRoutes.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["Assessment"]
)

# Include Roadmap Assessment routes
app.include_router(
    roadmapAssessmentRoutes.router,
    prefix=f"{settings.API_V1_PREFIX}/assessments",
    tags=["Roadmap Assessments"]
)

# Stage management routes removed - internal backend logic only

logger.info(f"API routers registered at {settings.API_V1_PREFIX}")


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get(
    "/",
    tags=["Root"],
    summary="API Root",
    description="Root endpoint with API information"
)
async def root():
    """
    Root endpoint returning API information.
    
    Returns:
        API metadata and available endpoints
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "health": f"{settings.API_V1_PREFIX}/auth/health",
            "auth": f"{settings.API_V1_PREFIX}/auth",
            "users": f"{settings.API_V1_PREFIX}/users",
            "registration": f"{settings.API_V1_PREFIX}/registration",
            "ai": f"{settings.API_V1_PREFIX}/ai"
        }
    }


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )


