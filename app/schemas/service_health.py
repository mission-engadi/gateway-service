"""Service Health Schemas"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class ServiceStatus(str, Enum):
    """Service health status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class ServiceHealthBase(BaseModel):
    """Base service health schema"""
    service_name: str = Field(..., description="Service name")
    service_url: str = Field(..., description="Service URL")
    status: ServiceStatus = Field(..., description="Service status")
    last_check_at: Optional[datetime] = Field(None, description="Last health check time")
    response_time: Optional[float] = Field(None, description="Response time in milliseconds")
    error_count: int = Field(0, description="Error count")
    success_count: int = Field(0, description="Success count")
    circuit_open: bool = Field(False, description="Circuit breaker status")


class ServiceHealthCreate(BaseModel):
    """Schema for creating service health record"""
    service_name: str
    service_url: str


class ServiceHealthUpdate(BaseModel):
    """Schema for updating service health"""
    service_url: Optional[str] = None
    status: Optional[ServiceStatus] = None
    last_check_at: Optional[datetime] = None
    response_time: Optional[float] = None
    error_count: Optional[int] = None
    success_count: Optional[int] = None
    circuit_open: Optional[bool] = None


class ServiceHealthResponse(ServiceHealthBase):
    """Schema for service health response"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AggregatedHealthResponse(BaseModel):
    """Aggregated health status for all services"""
    overall_status: ServiceStatus
    total_services: int
    healthy_services: int
    unhealthy_services: int
    degraded_services: int
    services: list[ServiceHealthResponse]
