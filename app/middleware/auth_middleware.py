"""Auth Middleware"""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.auth_service import AuthService
from app.db.session import AsyncSessionLocal
from app.services.routing_service import RoutingService


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for JWT authentication"""
    
    def __init__(self, app):
        super().__init__(app)
        self.auth_service = AuthService()
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        public_paths = [
            "/health",
            "/api/v1/gateway/health",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
        
        if request.url.path in public_paths:
            return await call_next(request)
        
        # Check if route is public
        async with AsyncSessionLocal() as db:
            routing_service = RoutingService(db)
            is_public = await routing_service.is_public_route(
                path=request.url.path,
                method=request.method
            )
        
        if is_public:
            return await call_next(request)
        
        # Get authorization header
        authorization = request.headers.get("Authorization")
        
        if not authorization:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "unauthorized",
                    "message": "Missing authorization header"
                }
            )
        
        # Validate token
        user_context = await self.auth_service.get_user_context(authorization)
        
        if not user_context:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "unauthorized",
                    "message": "Invalid or expired token"
                }
            )
        
        # Add user context to request state
        request.state.user_context = user_context
        request.state.user_id = user_context.get('user_id')
        
        return await call_next(request)
