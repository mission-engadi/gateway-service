"""Rate Limit Rule Schemas"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class LimitType(str, Enum):
    """Rate limit type"""
    PER_USER = "per_user"
    PER_IP = "per_ip"
    PER_ENDPOINT = "per_endpoint"
    GLOBAL = "global"


class RateLimitRuleBase(BaseModel):
    """Base rate limit rule schema"""
    rule_name: str = Field(..., description="Unique rule name")
    limit_type: LimitType = Field(..., description="Type of rate limit")
    path_pattern: Optional[str] = Field(None, description="Path pattern (null = all paths)")
    max_requests: int = Field(..., description="Maximum requests allowed", gt=0)
    window_seconds: int = Field(..., description="Time window in seconds", gt=0)
    is_active: bool = Field(True, description="Whether rule is active")


class RateLimitRuleCreate(RateLimitRuleBase):
    """Schema for creating rate limit rule"""
    pass


class RateLimitRuleUpdate(BaseModel):
    """Schema for updating rate limit rule"""
    rule_name: Optional[str] = None
    limit_type: Optional[LimitType] = None
    path_pattern: Optional[str] = None
    max_requests: Optional[int] = Field(None, gt=0)
    window_seconds: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None


class RateLimitRuleResponse(RateLimitRuleBase):
    """Schema for rate limit rule response"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RateLimitStatus(BaseModel):
    """Rate limit status for a client"""
    key: str = Field(..., description="Rate limit key (user_id, IP, etc.)")
    limit_type: LimitType
    current_requests: int = Field(..., description="Current request count")
    max_requests: int
    window_seconds: int
    remaining: int = Field(..., description="Remaining requests")
    reset_at: datetime = Field(..., description="When the limit resets")
