"""Proxy Request/Response Schemas"""
from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ProxyRequest(BaseModel):
    """Proxy request schema"""
    method: str = Field(..., description="HTTP method")
    path: str = Field(..., description="Request path")
    headers: Dict[str, str] = Field(default_factory=dict, description="Request headers")
    query_params: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    body: Optional[Any] = Field(None, description="Request body")
    user_id: Optional[UUID] = Field(None, description="Authenticated user ID")


class ProxyResponse(BaseModel):
    """Proxy response schema"""
    status_code: int = Field(..., description="Response status code")
    headers: Dict[str, str] = Field(default_factory=dict, description="Response headers")
    body: Any = Field(..., description="Response body")
    response_time: float = Field(..., description="Response time in milliseconds")
    target_service: str = Field(..., description="Target service name")


class GatewayError(BaseModel):
    """Gateway error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    request_id: UUID = Field(..., description="Request ID for tracking")
    timestamp: str = Field(..., description="Error timestamp")
