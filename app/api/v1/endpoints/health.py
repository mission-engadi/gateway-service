"""Health check endpoints.

Provides endpoints for monitoring service health and readiness.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Basic health check",
    description="Returns basic service health status without dependencies",
)
async def health_check():
    """Basic health check endpoint.
    
    This endpoint always returns 200 OK if the service is running.
    It doesn't check dependencies like database or external services.
    Use this for basic monitoring and load balancer health checks.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Returns service readiness including database connectivity",
)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check endpoint.
    
    This endpoint checks if the service is ready to handle requests.
    It verifies database connectivity and other critical dependencies.
    Use this for Kubernetes readiness probes.
    """
    checks = {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "ready",
        "checks": {},
    }
    
    # Check database connectivity
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        checks["checks"]["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        checks["checks"]["database"] = "disconnected"
        checks["status"] = "not ready"
    
    # Add more dependency checks here (Redis, Kafka, etc.)
    
    # Return appropriate status code
    if checks["status"] == "not ready":
        return checks, status.HTTP_503_SERVICE_UNAVAILABLE
    
    return checks
