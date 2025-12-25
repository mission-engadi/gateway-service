"""Route Configuration Model"""
from datetime import datetime
from typing import List
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base_class import Base


class RouteConfig(Base):
    """Route Configuration for API Gateway routing"""
    __tablename__ = "route_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path_pattern = Column(String, nullable=False, unique=True, index=True)  # e.g., "/api/v1/auth/*"
    target_service = Column(String, nullable=False)  # Service name
    target_url = Column(String, nullable=False)  # Full service URL
    methods = Column(ARRAY(String), nullable=False)  # HTTP methods allowed
    is_public = Column(Boolean, default=False)  # Requires auth or not
    is_active = Column(Boolean, default=True, index=True)
    priority = Column(Integer, default=0, index=True)  # Route matching priority (higher = first)
    timeout = Column(Integer, default=30)  # Request timeout in seconds
    retry_count = Column(Integer, default=3)  # Retry attempts
    circuit_breaker_enabled = Column(Boolean, default=True)  # Enable circuit breaker
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<RouteConfig(path_pattern='{self.path_pattern}', target_service='{self.target_service}', methods={self.methods})>"
