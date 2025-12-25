"""Gateway Management Endpoints"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.routing_service import RoutingService
from app.services.health_service import HealthService
from app.services.circuit_breaker_service import CircuitBreakerService
from app.services.logging_service import LoggingService
from app.schemas.route_config import RouteConfigCreate, RouteConfigUpdate, RouteConfigResponse
from app.schemas.service_health import ServiceHealthResponse, AggregatedHealthResponse
from app.schemas.gateway_stats import GatewayStatsResponse

router = APIRouter()

# Global circuit breaker service instance
circuit_breaker_service = CircuitBreakerService()


@router.get("/routes", response_model=List[RouteConfigResponse])
async def get_all_routes(
    active_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all route configurations.
    
    - **active_only**: If True, return only active routes
    """
    routing_service = RoutingService(db)
    routes = await routing_service.get_all_routes(active_only=active_only)
    return routes


@router.post("/routes", response_model=RouteConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_route(
    route_data: RouteConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new route configuration.
    
    This endpoint allows administrators to add new routing rules to the gateway.
    """
    routing_service = RoutingService(db)
    try:
        route = await routing_service.create_route(route_data)
        return route
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create route: {str(e)}"
        )


@router.put("/routes/{route_id}", response_model=RouteConfigResponse)
async def update_route(
    route_id: UUID,
    route_data: RouteConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing route configuration.
    
    - **route_id**: UUID of the route to update
    """
    routing_service = RoutingService(db)
    route = await routing_service.update_route(str(route_id), route_data)
    
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found"
        )
    
    return route


@router.delete("/routes/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_route(
    route_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a route configuration.
    
    - **route_id**: UUID of the route to delete
    """
    routing_service = RoutingService(db)
    success = await routing_service.delete_route(str(route_id))
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found"
        )
    
    return None


@router.get("/health", response_model=AggregatedHealthResponse)
async def get_gateway_health(
    db: AsyncSession = Depends(get_db)
):
    """
    Get aggregated health status of the gateway and all downstream services.
    """
    health_service = HealthService(db)
    health_status = await health_service.get_aggregated_health()
    await health_service.close()
    return health_status


@router.get("/services", response_model=List[ServiceHealthResponse])
async def get_all_services_health(
    db: AsyncSession = Depends(get_db)
):
    """
    Get health status of all registered services.
    """
    health_service = HealthService(db)
    services = await health_service.get_all_services_health()
    await health_service.close()
    return services


@router.post("/services/{service_name}/reset", response_model=ServiceHealthResponse)
async def reset_circuit_breaker(
    service_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset circuit breaker for a specific service.
    
    - **service_name**: Name of the service
    """
    health_service = HealthService(db)
    service = await health_service.reset_circuit_breaker(service_name)
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{service_name}' not found"
        )
    
    # Also reset in-memory circuit breaker
    circuit_breaker_service.reset(service_name)
    
    await health_service.close()
    return service


@router.get("/stats", response_model=GatewayStatsResponse)
async def get_gateway_stats(
    hours: int = 24,
    db: AsyncSession = Depends(get_db)
):
    """
    Get gateway statistics for a time period.
    
    - **hours**: Number of hours to analyze (default: 24)
    """
    logging_service = LoggingService(db)
    stats = await logging_service.get_gateway_stats(hours=hours)
    return stats
