"""Tests for routing service."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.routing_service import RoutingService
from app.models.route_config import RouteConfig


@pytest.mark.asyncio
class TestRoutingService:
    """Test routing service functionality."""
    
    async def test_get_route_by_path(self, db_session: AsyncSession, sample_route_config: dict):
        """Test getting route by path."""
        service = RoutingService(db_session)
        route = await service.get_route_by_path("/api/v1/test")
        
        assert route is not None
        assert route.path == "/api/v1/test"
        assert route.target_service == "test-service"
        assert route.is_active is True
    
    async def test_get_route_not_found(self, db_session: AsyncSession):
        """Test getting non-existent route."""
        service = RoutingService(db_session)
        route = await service.get_route_by_path("/nonexistent")
        
        assert route is None
    
    async def test_get_all_active_routes(self, db_session: AsyncSession, sample_route_config: dict):
        """Test getting all active routes."""
        service = RoutingService(db_session)
        routes = await service.get_all_active_routes()
        
        assert len(routes) > 0
        assert all(route.is_active for route in routes)
    
    async def test_create_route(self, db_session: AsyncSession):
        """Test creating new route."""
        service = RoutingService(db_session)
        
        route_data = {
            "path": "/api/v1/new",
            "target_service": "new-service",
            "target_url": "http://new-service:8000",
            "methods": ["GET"],
            "auth_required": False,
            "rate_limit": 50
        }
        
        route = await service.create_route(route_data)
        
        assert route.id is not None
        assert route.path == "/api/v1/new"
        assert route.target_service == "new-service"
    
    async def test_update_route(self, db_session: AsyncSession, sample_route_config: dict):
        """Test updating existing route."""
        service = RoutingService(db_session)
        
        update_data = {"rate_limit": 200}
        route = await service.update_route(sample_route_config["id"], update_data)
        
        assert route.rate_limit == 200
    
    async def test_delete_route(self, db_session: AsyncSession, sample_route_config: dict):
        """Test deleting route."""
        service = RoutingService(db_session)
        
        result = await service.delete_route(sample_route_config["id"])
        assert result is True
        
        # Verify route is deleted
        route = await service.get_route_by_path(sample_route_config["path"])
        assert route is None
    
    async def test_match_route(self, db_session: AsyncSession, sample_route_config: dict):
        """Test route matching logic."""
        service = RoutingService(db_session)
        
        # Exact match
        route = await service.match_route("/api/v1/test")
        assert route is not None
        
        # No match
        route = await service.match_route("/api/v1/other")
        assert route is None


@pytest.mark.asyncio
class TestRoutingEndpoints:
    """Test routing API endpoints."""
    
    async def test_get_routes(self, client: AsyncClient, mock_headers: dict, sample_route_config: dict):
        """Test GET /api/v1/routes endpoint."""
        response = await client.get("/api/v1/routes", headers=mock_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    async def test_create_route_endpoint(self, client: AsyncClient, mock_headers: dict):
        """Test POST /api/v1/routes endpoint."""
        route_data = {
            "path": "/api/v1/endpoint",
            "target_service": "endpoint-service",
            "target_url": "http://endpoint-service:8000",
            "methods": ["GET", "POST"],
            "auth_required": True,
            "rate_limit": 100
        }
        
        response = await client.post("/api/v1/routes", json=route_data, headers=mock_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["path"] == route_data["path"]
    
    async def test_update_route_endpoint(self, client: AsyncClient, mock_headers: dict, sample_route_config: dict):
        """Test PUT /api/v1/routes/{id} endpoint."""
        update_data = {"rate_limit": 150}
        
        response = await client.put(
            f"/api/v1/routes/{sample_route_config['id']}",
            json=update_data,
            headers=mock_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["rate_limit"] == 150
    
    async def test_delete_route_endpoint(self, client: AsyncClient, mock_headers: dict, sample_route_config: dict):
        """Test DELETE /api/v1/routes/{id} endpoint."""
        response = await client.delete(
            f"/api/v1/routes/{sample_route_config['id']}",
            headers=mock_headers
        )
        
        assert response.status_code == 204
