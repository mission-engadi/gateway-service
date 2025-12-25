"""Logging Service - Request/response logging and analytics"""
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.gateway_log import GatewayLog
from app.schemas.gateway_log import GatewayLogCreate, GatewayLogFilter
from app.schemas.gateway_stats import (
    GatewayStatsResponse,
    EndpointStats,
    ServiceStats,
    PerformanceMetrics
)


class LoggingService:
    """Service for logging and analytics"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log_request(
        self,
        request_id: UUID,
        method: str,
        path: str,
        target_service: Optional[str] = None,
        user_id: Optional[UUID] = None,
        client_ip: Optional[str] = None,
        status_code: Optional[int] = None,
        response_time: Optional[float] = None,
        error_message: Optional[str] = None
    ) -> GatewayLog:
        """Log a gateway request
        
        Args:
            request_id: Unique request ID
            method: HTTP method
            path: Request path
            target_service: Target service name
            user_id: User ID (if authenticated)
            client_ip: Client IP address
            status_code: Response status code
            response_time: Response time in milliseconds
            error_message: Error message (if any)
            
        Returns:
            Created GatewayLog
        """
        log = GatewayLog(
            request_id=request_id,
            method=method,
            path=path,
            target_service=target_service,
            user_id=user_id,
            client_ip=client_ip,
            status_code=status_code,
            response_time=response_time,
            error_message=error_message
        )
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log
    
    async def get_logs(
        self,
        filters: Optional[GatewayLogFilter] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[GatewayLog]:
        """Get gateway logs with optional filters
        
        Args:
            filters: Log filters
            limit: Maximum number of logs to return
            offset: Number of logs to skip
            
        Returns:
            List of GatewayLog
        """
        stmt = select(GatewayLog)
        
        if filters:
            if filters.method:
                stmt = stmt.where(GatewayLog.method == filters.method)
            if filters.path:
                stmt = stmt.where(GatewayLog.path.like(f"%{filters.path}%"))
            if filters.target_service:
                stmt = stmt.where(GatewayLog.target_service == filters.target_service)
            if filters.user_id:
                stmt = stmt.where(GatewayLog.user_id == filters.user_id)
            if filters.status_code:
                stmt = stmt.where(GatewayLog.status_code == filters.status_code)
            if filters.start_date:
                stmt = stmt.where(GatewayLog.created_at >= filters.start_date)
            if filters.end_date:
                stmt = stmt.where(GatewayLog.created_at <= filters.end_date)
            if filters.min_response_time:
                stmt = stmt.where(GatewayLog.response_time >= filters.min_response_time)
            if filters.max_response_time:
                stmt = stmt.where(GatewayLog.response_time <= filters.max_response_time)
        
        stmt = stmt.order_by(GatewayLog.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_error_logs(self, limit: int = 100) -> List[GatewayLog]:
        """Get recent error logs
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of error GatewayLog
        """
        stmt = select(GatewayLog).where(
            GatewayLog.error_message.isnot(None)
        ).order_by(GatewayLog.created_at.desc()).limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_gateway_stats(self, hours: int = 24) -> GatewayStatsResponse:
        """Get gateway statistics for a time period
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Gateway statistics
        """
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Total requests
        total_stmt = select(func.count(GatewayLog.id)).where(
            GatewayLog.created_at >= start_time
        )
        total_result = await self.db.execute(total_stmt)
        total_requests = total_result.scalar() or 0
        
        # Successful requests (2xx, 3xx)
        success_stmt = select(func.count(GatewayLog.id)).where(
            and_(
                GatewayLog.created_at >= start_time,
                GatewayLog.status_code >= 200,
                GatewayLog.status_code < 400
            )
        )
        success_result = await self.db.execute(success_stmt)
        successful_requests = success_result.scalar() or 0
        
        failed_requests = total_requests - successful_requests
        error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Average response time
        avg_time_stmt = select(func.avg(GatewayLog.response_time)).where(
            and_(
                GatewayLog.created_at >= start_time,
                GatewayLog.response_time.isnot(None)
            )
        )
        avg_time_result = await self.db.execute(avg_time_stmt)
        avg_response_time = avg_time_result.scalar() or 0
        
        # Requests per second
        time_diff = hours * 3600  # Convert to seconds
        requests_per_second = total_requests / time_diff if time_diff > 0 else 0
        
        # Top endpoints
        top_endpoints = await self._get_top_endpoints(start_time)
        
        # Service stats
        service_stats = await self._get_service_stats(start_time)
        
        return GatewayStatsResponse(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            top_endpoints=top_endpoints,
            service_stats=service_stats,
            time_period=f"Last {hours} hours",
            generated_at=datetime.utcnow()
        )
    
    async def _get_top_endpoints(self, start_time: datetime, limit: int = 10) -> List[EndpointStats]:
        """Get top endpoints by traffic"""
        # This is a simplified version - in production, use more complex aggregations
        stmt = select(
            GatewayLog.path,
            func.count(GatewayLog.id).label('total'),
            func.avg(GatewayLog.response_time).label('avg_time'),
            func.min(GatewayLog.response_time).label('min_time'),
            func.max(GatewayLog.response_time).label('max_time')
        ).where(
            GatewayLog.created_at >= start_time
        ).group_by(GatewayLog.path).order_by(func.count(GatewayLog.id).desc()).limit(limit)
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        endpoints = []
        for row in rows:
            # Count successful vs failed
            success_stmt = select(func.count(GatewayLog.id)).where(
                and_(
                    GatewayLog.path == row.path,
                    GatewayLog.created_at >= start_time,
                    GatewayLog.status_code >= 200,
                    GatewayLog.status_code < 400
                )
            )
            success_result = await self.db.execute(success_stmt)
            successful = success_result.scalar() or 0
            
            endpoints.append(EndpointStats(
                path=row.path,
                total_requests=row.total,
                successful_requests=successful,
                failed_requests=row.total - successful,
                avg_response_time=row.avg_time or 0,
                min_response_time=row.min_time or 0,
                max_response_time=row.max_time or 0
            ))
        
        return endpoints
    
    async def _get_service_stats(self, start_time: datetime) -> List[ServiceStats]:
        """Get statistics per service"""
        stmt = select(
            GatewayLog.target_service,
            func.count(GatewayLog.id).label('total'),
            func.avg(GatewayLog.response_time).label('avg_time')
        ).where(
            and_(
                GatewayLog.created_at >= start_time,
                GatewayLog.target_service.isnot(None)
            )
        ).group_by(GatewayLog.target_service)
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        services = []
        for row in rows:
            # Count successful vs failed
            success_stmt = select(func.count(GatewayLog.id)).where(
                and_(
                    GatewayLog.target_service == row.target_service,
                    GatewayLog.created_at >= start_time,
                    GatewayLog.status_code >= 200,
                    GatewayLog.status_code < 400
                )
            )
            success_result = await self.db.execute(success_stmt)
            successful = success_result.scalar() or 0
            
            failed = row.total - successful
            error_rate = (failed / row.total * 100) if row.total > 0 else 0
            
            services.append(ServiceStats(
                service_name=row.target_service,
                total_requests=row.total,
                successful_requests=successful,
                failed_requests=failed,
                avg_response_time=row.avg_time or 0,
                error_rate=error_rate
            ))
        
        return services
    
    async def get_performance_metrics(self, hours: int = 24) -> PerformanceMetrics:
        """Get performance metrics (percentiles)
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Performance metrics
        """
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Get all response times
        stmt = select(GatewayLog.response_time).where(
            and_(
                GatewayLog.created_at >= start_time,
                GatewayLog.response_time.isnot(None)
            )
        ).order_by(GatewayLog.response_time)
        
        result = await self.db.execute(stmt)
        response_times = [row[0] for row in result.all()]
        
        if not response_times:
            return PerformanceMetrics(
                p50_response_time=0,
                p90_response_time=0,
                p95_response_time=0,
                p99_response_time=0,
                total_requests=0,
                time_period=f"Last {hours} hours"
            )
        
        # Calculate percentiles
        total = len(response_times)
        p50_idx = int(total * 0.50)
        p90_idx = int(total * 0.90)
        p95_idx = int(total * 0.95)
        p99_idx = int(total * 0.99)
        
        return PerformanceMetrics(
            p50_response_time=response_times[p50_idx] if p50_idx < total else response_times[-1],
            p90_response_time=response_times[p90_idx] if p90_idx < total else response_times[-1],
            p95_response_time=response_times[p95_idx] if p95_idx < total else response_times[-1],
            p99_response_time=response_times[p99_idx] if p99_idx < total else response_times[-1],
            total_requests=total,
            time_period=f"Last {hours} hours"
        )
