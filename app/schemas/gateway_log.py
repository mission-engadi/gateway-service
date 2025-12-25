"""Gateway Log Schemas"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class GatewayLogBase(BaseModel):
    """Base gateway log schema"""
    request_id: UUID = Field(..., description="Unique request ID")
    method: str = Field(..., description="HTTP method")
    path: str = Field(..., description="Request path")
    target_service: Optional[str] = Field(None, description="Target service name")
    user_id: Optional[UUID] = Field(None, description="User ID (if authenticated)")
    client_ip: Optional[str] = Field(None, description="Client IP address")
    status_code: Optional[int] = Field(None, description="Response status code")
    response_time: Optional[float] = Field(None, description="Response time in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message (if any)")


class GatewayLogCreate(GatewayLogBase):
    """Schema for creating gateway log"""
    pass


class GatewayLogResponse(GatewayLogBase):
    """Schema for gateway log response"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class GatewayLogFilter(BaseModel):
    """Schema for filtering gateway logs"""
    method: Optional[str] = None
    path: Optional[str] = None
    target_service: Optional[str] = None
    user_id: Optional[UUID] = None
    status_code: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_response_time: Optional[float] = None
    max_response_time: Optional[float] = None
