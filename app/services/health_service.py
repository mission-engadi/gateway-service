"""Health Service - Service health monitoring"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.service_health import ServiceHealth, ServiceStatus
from app.schemas.service_health import ServiceHealthCreate, ServiceHealthUpdate, AggregatedHealthResponse
from app.services.proxy_service import ProxyService


class HealthService:
    """Service for monitoring downstream service health"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.proxy_service = ProxyService()
    
    async def check_service_health(self, service_name: str) -> Optional[ServiceHealth]:
        """Check health of a specific service
        
        Args:
            service_name: Name of the service
            
        Returns:
            Updated ServiceHealth record
        """
        # Get service record
        stmt = select(ServiceHealth).where(ServiceHealth.service_name == service_name)
        result = await self.db.execute(stmt)
        service = result.scalar_one_or_none()
        
        if not service:
            return None
        
        # Perform health check
        is_healthy, response_time = await self.proxy_service.health_check(service.service_url)
        
        # Update service record
        service.last_check_at = datetime.utcnow()
        service.response_time = response_time
        
        if is_healthy:
            service.status = ServiceStatus.HEALTHY
            service.success_count += 1
            # Reset circuit if it was open and we have enough successes
            if service.circuit_open and service.success_count > 5:
                service.circuit_open = False
                service.error_count = 0
        else:
            service.error_count += 1
            
            # Determine status based on error count
            if service.error_count >= 5:
                service.status = ServiceStatus.UNHEALTHY
                service.circuit_open = True
            elif service.error_count >= 2:
                service.status = ServiceStatus.DEGRADED
        
        await self.db.commit()
        await self.db.refresh(service)
        return service
    
    async def check_all_services(self) -> List[ServiceHealth]:
        """Check health of all registered services
        
        Returns:
            List of updated ServiceHealth records
        """
        stmt = select(ServiceHealth)
        result = await self.db.execute(stmt)
        services = result.scalars().all()
        
        updated_services = []
        for service in services:
            updated = await self.check_service_health(service.service_name)
            if updated:
                updated_services.append(updated)
        
        return updated_services
    
    async def get_service_health(self, service_name: str) -> Optional[ServiceHealth]:
        """Get health status of a service"""
        stmt = select(ServiceHealth).where(ServiceHealth.service_name == service_name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all_services_health(self) -> List[ServiceHealth]:
        """Get health status of all services"""
        stmt = select(ServiceHealth)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_aggregated_health(self) -> AggregatedHealthResponse:
        """Get aggregated health status
        
        Returns:
            Aggregated health response
        """
        services = await self.get_all_services_health()
        
        healthy = sum(1 for s in services if s.status == ServiceStatus.HEALTHY)
        unhealthy = sum(1 for s in services if s.status == ServiceStatus.UNHEALTHY)
        degraded = sum(1 for s in services if s.status == ServiceStatus.DEGRADED)
        
        # Determine overall status
        if unhealthy > 0:
            overall_status = ServiceStatus.UNHEALTHY
        elif degraded > 0:
            overall_status = ServiceStatus.DEGRADED
        elif healthy == len(services):
            overall_status = ServiceStatus.HEALTHY
        else:
            overall_status = ServiceStatus.UNKNOWN
        
        return AggregatedHealthResponse(
            overall_status=overall_status,
            total_services=len(services),
            healthy_services=healthy,
            unhealthy_services=unhealthy,
            degraded_services=degraded,
            services=[ServiceHealthResponse.model_validate(s) for s in services]
        )
    
    async def register_service(self, service_data: ServiceHealthCreate) -> ServiceHealth:
        """Register a new service for health monitoring"""
        service = ServiceHealth(
            service_name=service_data.service_name,
            service_url=service_data.service_url,
            status=ServiceStatus.UNKNOWN
        )
        self.db.add(service)
        await self.db.commit()
        await self.db.refresh(service)
        return service
    
    async def reset_circuit_breaker(self, service_name: str) -> Optional[ServiceHealth]:
        """Reset circuit breaker for a service
        
        Args:
            service_name: Name of the service
            
        Returns:
            Updated ServiceHealth record
        """
        service = await self.get_service_health(service_name)
        if not service:
            return None
        
        service.circuit_open = False
        service.error_count = 0
        service.status = ServiceStatus.UNKNOWN
        
        await self.db.commit()
        await self.db.refresh(service)
        return service
    
    async def is_circuit_open(self, service_name: str) -> bool:
        """Check if circuit breaker is open for a service
        
        Args:
            service_name: Name of the service
            
        Returns:
            True if circuit is open, False otherwise
        """
        service = await self.get_service_health(service_name)
        if service:
            return service.circuit_open
        return False
    
    async def close(self):
        """Close proxy service client"""
        await self.proxy_service.close()


# Fix import
from app.schemas.service_health import ServiceHealthResponse
