"""Application configuration using Pydantic settings.

Configuration is loaded from environment variables or .env file.
Different configurations can be used for dev/staging/prod environments.
"""

import secrets
from typing import List, Optional

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.
    
    All settings can be overridden via environment variables.
    For example, DATABASE_URL can be set in the environment or .env file.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    # Application
    PROJECT_NAME: str = "Gateway Service"
    PROJECT_DESCRIPTION: str = "API Gateway for Mission Engadi microservices architecture"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8000
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)  # Override in production!
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://engadi.org",
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/gateway_service_db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis (for caching, sessions, etc.)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Kafka (for event-driven architecture)
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_PREFIX: str = "gateway_service"
    
    # External Services - All Mission Engadi Microservices
    AUTH_SERVICE_URL: str = "http://localhost:8002"
    CONTENT_SERVICE_URL: str = "http://localhost:8003"
    PARTNERS_CRM_SERVICE_URL: str = "http://localhost:8005"
    PROJECTS_SERVICE_URL: str = "http://localhost:8006"
    SOCIAL_MEDIA_SERVICE_URL: str = "http://localhost:8007"
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8008"
    ANALYTICS_SERVICE_URL: str = "http://localhost:8009"
    AI_SERVICE_URL: str = "http://localhost:8010"
    SEARCH_SERVICE_URL: str = "http://localhost:8011"
    
    # Gateway Settings
    GATEWAY_TIMEOUT: int = 30  # Default timeout in seconds
    GATEWAY_RETRY_COUNT: int = 3  # Default retry count
    GATEWAY_MAX_CONNECTIONS: int = 100  # Max concurrent connections
    
    # Rate Limiting Settings
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_USER: int = 1000  # Requests per window
    RATE_LIMIT_PER_IP: int = 500  # Requests per window
    RATE_LIMIT_WINDOW: int = 3600  # Window in seconds (1 hour)
    
    # Circuit Breaker Settings
    CIRCUIT_BREAKER_ENABLED: bool = True
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5  # Failures before opening
    CIRCUIT_BREAKER_SUCCESS_THRESHOLD: int = 2  # Successes to close from half-open
    CIRCUIT_BREAKER_TIMEOUT: int = 60  # Seconds before trying half-open
    
    # Health Check Settings
    HEALTH_CHECK_INTERVAL: int = 60  # Seconds between health checks
    HEALTH_CHECK_TIMEOUT: int = 5  # Health check timeout
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    GATEWAY_LOG_RETENTION_DAYS: int = 30  # Days to retain gateway logs
    
    # Monitoring
    DATADOG_API_KEY: Optional[str] = None
    DATADOG_APP_KEY: Optional[str] = None
    
    # Feature Flags
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = False
    ENABLE_REQUEST_LOGGING: bool = True
    

# Create global settings instance
settings = Settings()
