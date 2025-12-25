"""Rate Limit Rule Model"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.db.base_class import Base


class LimitType(str, enum.Enum):
    """Rate limit type"""
    PER_USER = "per_user"
    PER_IP = "per_ip"
    PER_ENDPOINT = "per_endpoint"
    GLOBAL = "global"


class RateLimitRule(Base):
    """Rate Limit Rule for API Gateway"""
    __tablename__ = "rate_limit_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_name = Column(String, nullable=False, unique=True, index=True)
    limit_type = Column(SQLEnum(LimitType), nullable=False, index=True)
    path_pattern = Column(String, nullable=True)  # Apply to specific paths (null = all paths)
    max_requests = Column(Integer, nullable=False)  # Max requests
    window_seconds = Column(Integer, nullable=False)  # Time window in seconds
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<RateLimitRule(rule_name='{self.rule_name}', type={self.limit_type}, max={self.max_requests}/{self.window_seconds}s)>"
