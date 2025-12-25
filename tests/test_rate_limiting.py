"""Tests for rate limiting service."""
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.rate_limit_service import RateLimitService
from app.models.rate_limit_rule import RateLimitRule


@pytest.mark.asyncio
class TestRateLimitService:
    """Test rate limiting service functionality."""
    
    async def test_check_rate_limit_allowed(self, db_session: AsyncSession, sample_rate_limit_rule: dict):
        """Test rate limit check when within limits."""
        service = RateLimitService(db_session)
        
        result = await service.check_rate_limit(
            path="/api/v1/test",
            client_id="user123"
        )
        
        assert result["allowed"] is True
        assert result["remaining"] > 0
    
    async def test_check_rate_limit_exceeded(self, db_session: AsyncSession):
        """Test rate limit check when exceeded."""
        service = RateLimitService(db_session)
        
        # Create rule with very low limit
        rule = RateLimitRule(
            path="/api/v1/limited",
            limit=2,
            window=60,
            is_active=True
        )
        db_session.add(rule)
        await db_session.commit()
        
        # Make requests up to limit
        for i in range(2):
            result = await service.check_rate_limit(
                path="/api/v1/limited",
                client_id="user456"
            )
            assert result["allowed"] is True
        
        # Next request should be rate limited
        result = await service.check_rate_limit(
            path="/api/v1/limited",
            client_id="user456"
        )
        
        assert result["allowed"] is False
        assert result["remaining"] == 0
    
    async def test_get_rate_limit_info(self, db_session: AsyncSession, sample_rate_limit_rule: dict):
        """Test getting rate limit information."""
        service = RateLimitService(db_session)
        
        info = await service.get_rate_limit_info(
            path="/api/v1/test",
            client_id="user789"
        )
        
        assert "limit" in info
        assert "remaining" in info
        assert "reset_time" in info
    
    async def test_reset_rate_limit(self, db_session: AsyncSession, sample_rate_limit_rule: dict):
        """Test resetting rate limit for a client."""
        service = RateLimitService(db_session)
        
        # Use some quota
        await service.check_rate_limit(
            path="/api/v1/test",
            client_id="user999"
        )
        
        # Reset
        await service.reset_rate_limit(
            path="/api/v1/test",
            client_id="user999"
        )
        
        # Check info
        info = await service.get_rate_limit_info(
            path="/api/v1/test",
            client_id="user999"
        )
        
        assert info["remaining"] == info["limit"]
    
    async def test_get_all_rules(self, db_session: AsyncSession, sample_rate_limit_rule: dict):
        """Test getting all rate limit rules."""
        service = RateLimitService(db_session)
        
        rules = await service.get_all_rules()
        
        assert len(rules) > 0
        assert all(isinstance(rule, RateLimitRule) for rule in rules)
    
    async def test_create_rule(self, db_session: AsyncSession):
        """Test creating new rate limit rule."""
        service = RateLimitService(db_session)
        
        rule_data = {
            "path": "/api/v1/newrule",
            "limit": 50,
            "window": 60,
            "is_active": True
        }
        
        rule = await service.create_rule(rule_data)
        
        assert rule.id is not None
        assert rule.path == "/api/v1/newrule"
        assert rule.limit == 50
    
    async def test_update_rule(self, db_session: AsyncSession, sample_rate_limit_rule: dict):
        """Test updating rate limit rule."""
        service = RateLimitService(db_session)
        
        update_data = {"limit": 200}
        rule = await service.update_rule(sample_rate_limit_rule["id"], update_data)
        
        assert rule.limit == 200
    
    async def test_delete_rule(self, db_session: AsyncSession, sample_rate_limit_rule: dict):
        """Test deleting rate limit rule."""
        service = RateLimitService(db_session)
        
        result = await service.delete_rule(sample_rate_limit_rule["id"])
        assert result is True


@pytest.mark.asyncio
class TestRateLimitEndpoints:
    """Test rate limiting API endpoints."""
    
    async def test_get_rate_limits(self, client: AsyncClient, mock_headers: dict, sample_rate_limit_rule: dict):
        """Test GET /api/v1/rate-limits endpoint."""
        response = await client.get("/api/v1/rate-limits", headers=mock_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_create_rate_limit(self, client: AsyncClient, mock_headers: dict):
        """Test POST /api/v1/rate-limits endpoint."""
        rule_data = {
            "path": "/api/v1/test-limit",
            "limit": 100,
            "window": 60,
            "is_active": True
        }
        
        response = await client.post("/api/v1/rate-limits", json=rule_data, headers=mock_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["path"] == rule_data["path"]
