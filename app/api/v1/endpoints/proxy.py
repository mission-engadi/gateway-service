"""Gateway Proxy Endpoint - Catch-all routing"""
import uuid
from typing import Any
from fastapi import APIRouter, Request, Response, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.routing_service import RoutingService
from app.services.proxy_service import ProxyService
from app.services.circuit_breaker_service import CircuitBreakerService
from app.schemas.proxy import GatewayError

router = APIRouter()

# Global instances
proxy_service = ProxyService()
circuit_breaker_service = CircuitBreakerService()


@router.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy_request(
    request: Request,
    full_path: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Catch-all proxy endpoint that routes requests to appropriate services.
    
    This endpoint:
    1. Matches the request to a route configuration
    2. Checks circuit breaker status
    3. Forwards the request to the target service
    4. Returns the response
    """
    # Get request ID from state (set by logging middleware)
    request_id = request.state.request_id if hasattr(request.state, 'request_id') else uuid.uuid4()
    
    # Reconstruct full path with leading slash
    path = f"/{full_path}" if not full_path.startswith('/') else full_path
    
    try:
        # Match route
        routing_service = RoutingService(db)
        route = await routing_service.match_route(path, request.method)
        
        if not route:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "route_not_found",
                    "message": f"No route configured for {request.method} {path}",
                    "request_id": str(request_id)
                }
            )
        
        # Store target service in request state for logging
        request.state.target_service = route.target_service
        
        # Check circuit breaker
        if route.circuit_breaker_enabled:
            if not circuit_breaker_service.is_available(route.target_service):
                return JSONResponse(
                    status_code=503,
                    content={
                        "error": "service_unavailable",
                        "message": f"Service '{route.target_service}' is currently unavailable (circuit breaker open)",
                        "request_id": str(request_id),
                        "target_service": route.target_service
                    }
                )
        
        # Get request body
        body = None
        content_type = request.headers.get('content-type', '')
        if content_type.startswith('application/json'):
            try:
                body = await request.json()
            except Exception:
                body = None
        
        # Get user ID from state (set by auth middleware)
        user_id = request.state.user_id if hasattr(request.state, 'user_id') else None
        
        # Forward request
        try:
            proxy_response = await proxy_service.forward_request(
                target_url=route.target_url,
                method=request.method,
                path=path,
                headers=dict(request.headers),
                query_params=dict(request.query_params),
                body=body,
                user_id=user_id,
                request_id=request_id,
                timeout=route.timeout,
                retry_count=route.retry_count
            )
            
            # Record success in circuit breaker
            if route.circuit_breaker_enabled:
                circuit_breaker_service.record_success(route.target_service)
            
            # Return response
            return JSONResponse(
                status_code=proxy_response.status_code,
                content=proxy_response.body,
                headers={
                    "X-Request-ID": str(request_id),
                    "X-Target-Service": proxy_response.target_service,
                    "X-Response-Time": f"{proxy_response.response_time:.2f}ms"
                }
            )
            
        except Exception as e:
            # Record failure in circuit breaker
            if route.circuit_breaker_enabled:
                circuit_breaker_service.record_failure(route.target_service)
            
            # Return error
            return JSONResponse(
                status_code=502,
                content={
                    "error": "bad_gateway",
                    "message": f"Failed to communicate with service '{route.target_service}': {str(e)}",
                    "request_id": str(request_id),
                    "target_service": route.target_service
                }
            )
    
    except Exception as e:
        # Unexpected error
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": f"Internal gateway error: {str(e)}",
                "request_id": str(request_id)
            }
        )
