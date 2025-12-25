"""Gateway Log Model"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base_class import Base


class GatewayLog(Base):
    """Gateway Request/Response Log"""
    __tablename__ = "gateway_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Unique request ID
    method = Column(String, nullable=False)
    path = Column(String, nullable=False, index=True)
    target_service = Column(String, nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    client_ip = Column(String, nullable=True, index=True)
    status_code = Column(Integer, nullable=True)
    response_time = Column(Float, nullable=True)  # Milliseconds
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<GatewayLog(request_id='{self.request_id}', method='{self.method}', path='{self.path}', status={self.status_code})>"
