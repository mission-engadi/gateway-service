"""Shared test fixtures for Gateway Service."""
import asyncio
import pytest
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.db.base_class import Base
from app.db.session import get_db
from app.core.config import settings

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False
)

# Create test session factory
TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create fresh database session for each test."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
    
    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database session override."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_auth_token() -> str:
    """Create mock authentication token."""
    return "Bearer test_token_12345"


@pytest.fixture
def mock_headers(mock_auth_token: str) -> dict:
    """Create mock headers with auth token."""
    return {
        "Authorization": mock_auth_token,
        "Content-Type": "application/json"
    }


@pytest.fixture
async def sample_route_config(db_session: AsyncSession) -> dict:
    """Create sample route configuration for testing."""
    from app.models.route_config import RouteConfig
    
    route = RouteConfig(
        path="/api/v1/test",
        target_service="test-service",
        target_url="http://test-service:8000",
        methods=["GET", "POST"],
        auth_required=True,
        rate_limit=100,
        is_active=True
    )
    
    db_session.add(route)
    await db_session.commit()
    await db_session.refresh(route)
    
    return {
        "id": route.id,
        "path": route.path,
        "target_url": route.target_url
    }


@pytest.fixture
async def sample_rate_limit_rule(db_session: AsyncSession) -> dict:
    """Create sample rate limit rule for testing."""
    from app.models.rate_limit_rule import RateLimitRule
    
    rule = RateLimitRule(
        path="/api/v1/test",
        limit=100,
        window=60,
        is_active=True
    )
    
    db_session.add(rule)
    await db_session.commit()
    await db_session.refresh(rule)
    
    return {
        "id": rule.id,
        "path": rule.path,
        "limit": rule.limit,
        "window": rule.window
    }
