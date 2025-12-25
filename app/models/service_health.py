"""Service Health Model"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.db.base_class import Base


class ServiceStatus(str, enum.Enum):
    """Service health status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class ServiceHealth(Base):
    """Service Health Monitoring"""
    __tablename__ = "service_health"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name = Column(String, nullable=False, unique=True, index=True)
    service_url = Column(String, nullable=False)
    status = Column(SQLEnum(ServiceStatus), nullable=False, default=ServiceStatus.UNKNOWN, index=True)
    last_check_at = Column(DateTime, nullable=True)
    response_time = Column(Float, nullable=True)  # Milliseconds
    error_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    circuit_open = Column(Boolean, default=False, index=True)  # Circuit breaker status
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ServiceHealth(service_name='{self.service_name}', status={self.status}, circuit_open={self.circuit_open})>"
