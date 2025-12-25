"""CORS Middleware"""
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware as FastAPICORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class CORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware wrapper
    
    Note: In production, you would typically use FastAPI's built-in CORS middleware
    or configure it in the main app. This is a wrapper for custom CORS logic.
    """
    
    async def dispatch(self, request: Request, call_next):
        # For now, just pass through to the built-in CORS middleware
        # Custom CORS logic can be added here if needed
        response = await call_next(request)
        
        # Add custom CORS headers if needed
        # response.headers["Access-Control-Allow-Origin"] = "*"
        # response.headers["Access-Control-Allow-Methods"] = "*"
        # response.headers["Access-Control-Allow-Headers"] = "*"
        
        return response


def setup_cors(app):
    """Setup CORS middleware for the application
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        FastAPICORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
