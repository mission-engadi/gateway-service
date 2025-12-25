"""Gateway Monitoring Endpoints"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.logging_service import LoggingService
from app.services.health_service import HealthService
from app.services.rate_limit_service import RateLimitService
from app.schemas.gateway_log import GatewayLogResponse, GatewayLogFilter
from app.schemas.gateway_stats import PerformanceMetrics
from app.schemas.service_health import ServiceHealthResponse
from app.schemas.rate_limit_rule import RateLimitRuleResponse

router = APIRouter()


@router.get("/logs", response_model=List[GatewayLogResponse])
async def get_gateway_logs(
    method: Optional[str] = None,
    path: Optional[str] = None,
    target_service: Optional[str] = None,
    user_id: Optional[UUID] = None,
    status_code: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get gateway request logs with optional filters.
    
    - **method**: Filter by HTTP method
    - **path**: Filter by request path (partial match)
    - **target_service**: Filter by target service
    - **user_id**: Filter by user ID
    - **status_code**: Filter by status code
    - **start_date**: Filter by start date
    - **end_date**: Filter by end date
    - **limit**: Maximum number of logs to return (1-1000)
    - **offset**: Number of logs to skip
    """
    filters = GatewayLogFilter(
        method=method,
        path=path,
        target_service=target_service,
        user_id=user_id,
        status_code=status_code,
        start_date=start_date,
        end_date=end_date
    )
    
    logging_service = LoggingService(db)
    logs = await logging_service.get_logs(filters=filters, limit=limit, offset=offset)
    return logs


@router.get("/metrics")
async def get_gateway_metrics(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    """
    Get gateway metrics and statistics.
    
    - **hours**: Number of hours to analyze (1-168, default: 24)
    """
    logging_service = LoggingService(db)
    stats = await logging_service.get_gateway_stats(hours=hours)
    return stats


@router.get("/errors", response_model=List[GatewayLogResponse])
async def get_error_logs(
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent error logs.
    
    - **limit**: Maximum number of error logs to return (1-1000)
    """
    logging_service = LoggingService(db)
    errors = await logging_service.get_error_logs(limit=limit)
    return errors


@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    """
    Get performance metrics (response time percentiles).
    
    - **hours**: Number of hours to analyze (1-168, default: 24)
    """
    logging_service = LoggingService(db)
    metrics = await logging_service.get_performance_metrics(hours=hours)
    return metrics


@router.get("/rate-limits", response_model=List[RateLimitRuleResponse])
async def get_rate_limits(
    db: AsyncSession = Depends(get_db)
):
    """
    Get current rate limit status and rules.
    """
    rate_limit_service = RateLimitService(db)
    rules = await rate_limit_service.get_rate_limit_rules()
    return rules


@router.get("/services/{service_name}/health", response_model=ServiceHealthResponse)
async def get_service_health(
    service_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed health information for a specific service.
    
    - **service_name**: Name of the service
    """
    health_service = HealthService(db)
    service = await health_service.get_service_health(service_name)
    
    if not service:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service_name}' not found"
        )
    
    # Perform a health check
    await health_service.check_service_health(service_name)
    service = await health_service.get_service_health(service_name)
    
    await health_service.close()
    return service
