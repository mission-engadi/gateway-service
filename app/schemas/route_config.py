"""Route Configuration Schemas"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class RouteConfigBase(BaseModel):
    """Base route configuration schema"""
    path_pattern: str = Field(..., description="Path pattern for routing, e.g., '/api/v1/auth/*'")
    target_service: str = Field(..., description="Target service name")
    target_url: str = Field(..., description="Full target service URL")
    methods: List[str] = Field(..., description="HTTP methods allowed")
    is_public: bool = Field(False, description="Whether route requires authentication")
    is_active: bool = Field(True, description="Whether route is active")
    priority: int = Field(0, description="Route matching priority (higher = first)")
    timeout: int = Field(30, description="Request timeout in seconds")
    retry_count: int = Field(3, description="Number of retry attempts")
    circuit_breaker_enabled: bool = Field(True, description="Enable circuit breaker")


class RouteConfigCreate(RouteConfigBase):
    """Schema for creating route configuration"""
    pass


class RouteConfigUpdate(BaseModel):
    """Schema for updating route configuration"""
    path_pattern: Optional[str] = None
    target_service: Optional[str] = None
    target_url: Optional[str] = None
    methods: Optional[List[str]] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    timeout: Optional[int] = None
    retry_count: Optional[int] = None
    circuit_breaker_enabled: Optional[bool] = None


class RouteConfigResponse(RouteConfigBase):
    """Schema for route configuration response"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
