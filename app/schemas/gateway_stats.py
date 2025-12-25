"""Gateway Statistics Schemas"""
from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel, Field


class EndpointStats(BaseModel):
    """Statistics for a specific endpoint"""
    path: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float  # milliseconds
    min_response_time: float
    max_response_time: float


class ServiceStats(BaseModel):
    """Statistics for a specific service"""
    service_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    error_rate: float  # percentage


class GatewayStatsResponse(BaseModel):
    """Overall gateway statistics"""
    total_requests: int = Field(..., description="Total requests processed")
    successful_requests: int = Field(..., description="Successful requests")
    failed_requests: int = Field(..., description="Failed requests")
    avg_response_time: float = Field(..., description="Average response time in milliseconds")
    requests_per_second: float = Field(..., description="Requests per second")
    error_rate: float = Field(..., description="Error rate percentage")
    top_endpoints: List[EndpointStats] = Field(..., description="Top endpoints by traffic")
    service_stats: List[ServiceStats] = Field(..., description="Statistics per service")
    time_period: str = Field(..., description="Time period for statistics")
    generated_at: datetime = Field(..., description="When statistics were generated")


class PerformanceMetrics(BaseModel):
    """Performance metrics"""
    p50_response_time: float = Field(..., description="50th percentile response time")
    p90_response_time: float = Field(..., description="90th percentile response time")
    p95_response_time: float = Field(..., description="95th percentile response time")
    p99_response_time: float = Field(..., description="99th percentile response time")
    total_requests: int
    time_period: str
