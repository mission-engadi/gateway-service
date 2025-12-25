"""Database base classes and common models."""

from sqlalchemy.orm import DeclarativeBase

# Import all models here for Alembic to detect them
from app.db.base_class import Base  # noqa: F401
from app.models.route_config import RouteConfig  # noqa: F401
from app.models.rate_limit_rule import RateLimitRule  # noqa: F401
from app.models.gateway_log import GatewayLog  # noqa: F401
from app.models.service_health import ServiceHealth  # noqa: F401
