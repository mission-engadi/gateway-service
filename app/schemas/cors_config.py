"""CORS Configuration Schemas"""
from typing import List
from pydantic import BaseModel, Field


class CORSConfig(BaseModel):
    """CORS configuration schema"""
    allowed_origins: List[str] = Field(
        default=["*"],
        description="Allowed origins for CORS"
    )
    allowed_methods: List[str] = Field(
        default=["*"],
        description="Allowed HTTP methods"
    )
    allowed_headers: List[str] = Field(
        default=["*"],
        description="Allowed headers"
    )
    allow_credentials: bool = Field(
        default=True,
        description="Allow credentials"
    )
    max_age: int = Field(
        default=600,
        description="Max age for preflight requests in seconds"
    )


class CORSConfigUpdate(BaseModel):
    """Schema for updating CORS configuration"""
    allowed_origins: List[str]
    allowed_methods: List[str]
    allowed_headers: List[str]
    allow_credentials: bool
    max_age: int
