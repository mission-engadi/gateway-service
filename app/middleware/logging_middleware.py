"""Logging Middleware"""
import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.db.session import AsyncSessionLocal
from app.services.logging_service import LoggingService


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = uuid.uuid4()
        request.state.request_id = request_id
        
        # Get client info
        client_ip = request.client.host if request.client else None
        user_id = request.state.user_id if hasattr(request.state, 'user_id') else None
        
        # Record start time
        start_time = time.time()
        
        # Process request
        response = None
        error_message = None
        status_code = None
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            error_message = str(e)
            status_code = 500
            raise
        finally:
            # Calculate response time
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Log request
            target_service = request.state.target_service if hasattr(request.state, 'target_service') else None
            
            async with AsyncSessionLocal() as db:
                logging_service = LoggingService(db)
                await logging_service.log_request(
                    request_id=request_id,
                    method=request.method,
                    path=request.url.path,
                    target_service=target_service,
                    user_id=user_id,
                    client_ip=client_ip,
                    status_code=status_code,
                    response_time=response_time,
                    error_message=error_message
                )
        
        # Add request ID to response headers
        if response:
            response.headers["X-Request-ID"] = str(request_id)
        
        return response
