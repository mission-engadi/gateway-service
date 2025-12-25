"""API router configuration.

This module aggregates all API routers for version 1.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health, management, monitoring, configuration, proxy

api_router = APIRouter()

# Include health check router (no prefix)
api_router.include_router(
    health.router,
    tags=["health"],
)

# Include gateway management router
api_router.include_router(
    management.router,
    prefix="/gateway",
    tags=["gateway-management"],
)

# Include monitoring router
api_router.include_router(
    monitoring.router,
    prefix="/gateway",
    tags=["gateway-monitoring"],
)

# Include configuration router
api_router.include_router(
    configuration.router,
    prefix="/gateway/config",
    tags=["gateway-configuration"],
)

# Include proxy router (this should be last as it catches all remaining paths)
# Note: Proxy router will handle all non-gateway requests
api_router.include_router(
    proxy.router,
    tags=["proxy"],
)
