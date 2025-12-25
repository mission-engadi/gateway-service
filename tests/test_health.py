"""Tests for health check endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.health_service import HealthService


@pytest.mark.asyncio
class TestHealthService:
    """Test health service functionality."""
    
    async def test_check_database_health(self, db_session: AsyncSession):
        """Test database health check."""
        service = HealthService(db_session)
        
        result = await service.check_database_health()
        
        assert result["status"] in ["healthy", "unhealthy"]
        assert "response_time" in result
    
    async def test_check_service_health(self, db_session: AsyncSession):
        """Test service health check."""
        service = HealthService(db_session)
        
        # Mock service URL
        result = await service.check_service_health(
            service_name="test-service",
            url="http://test-service:8000/health"
        )
        
        assert "status" in result
        assert "service_name" in result
    
    async def test_get_all_services_health(self, db_session: AsyncSession):
        """Test getting health of all services."""
        service = HealthService(db_session)
        
        results = await service.get_all_services_health()
        
        assert isinstance(results, list)
    
    async def test_record_health_check(self, db_session: AsyncSession):
        """Test recording health check result."""
        service = HealthService(db_session)
        
        health_data = {
            "service_name": "test-service",
            "status": "healthy",
            "response_time": 0.15,
            "error_message": None
        }
        
        record = await service.record_health_check(health_data)
        
        assert record.id is not None
        assert record.service_name == "test-service"
        assert record.status == "healthy"


@pytest.mark.asyncio
class TestHealthEndpoints:
    """Test health check endpoints."""
    
    async def test_health_check(self, client: AsyncClient):
        """Test GET /api/v1/health endpoint."""
        response = await client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
    
    async def test_readiness_check(self, client: AsyncClient):
        """Test GET /api/v1/ready endpoint."""
        response = await client.get("/api/v1/ready")
        
        assert response.status_code in [200, 503]
        data = response.json()
        assert "ready" in data
    
    async def test_liveness_check(self, client: AsyncClient):
        """Test GET /api/v1/live endpoint."""
        response = await client.get("/api/v1/live")
        
        assert response.status_code == 200
        data = response.json()
        assert "alive" in data
        assert data["alive"] is True
    
    async def test_services_health(self, client: AsyncClient, mock_headers: dict):
        """Test GET /api/v1/health/services endpoint."""
        response = await client.get("/api/v1/health/services", headers=mock_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
