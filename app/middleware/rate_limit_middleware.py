"""Rate Limit Middleware"""
import uuid
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.services.rate_limit_service import RateLimitService


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health check endpoints
        if request.url.path in ["/health", "/api/v1/gateway/health"]:
            return await call_next(request)
        
        # Get client info
        client_ip = request.client.host if request.client else None
        user_id = request.state.user_id if hasattr(request.state, 'user_id') else None
        
        # Check rate limit
        async with AsyncSessionLocal() as db:
            rate_limit_service = RateLimitService(db)
            is_allowed, rate_limit_status = await rate_limit_service.check_rate_limit(
                path=request.url.path,
                user_id=user_id,
                client_ip=client_ip
            )
        
        if not is_allowed and rate_limit_status:
            # Rate limit exceeded
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please try again later.",
                    "rate_limit": {
                        "limit": rate_limit_status.max_requests,
                        "remaining": rate_limit_status.remaining,
                        "reset_at": rate_limit_status.reset_at.isoformat(),
                        "window_seconds": rate_limit_status.window_seconds
                    }
                },
                headers={
                    "X-RateLimit-Limit": str(rate_limit_status.max_requests),
                    "X-RateLimit-Remaining": str(rate_limit_status.remaining),
                    "X-RateLimit-Reset": rate_limit_status.reset_at.isoformat(),
                    "Retry-After": str(rate_limit_status.window_seconds)
                }
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        
        if rate_limit_status:
            response.headers["X-RateLimit-Limit"] = str(rate_limit_status.max_requests)
            response.headers["X-RateLimit-Remaining"] = str(rate_limit_status.remaining)
            response.headers["X-RateLimit-Reset"] = rate_limit_status.reset_at.isoformat()
        
        return response
