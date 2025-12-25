"""Pydantic schemas for Example model.

Schemas define the structure of API requests and responses.
They provide validation and documentation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ExampleBase(BaseModel):
    """Base schema with common fields."""
    
    title: str = Field(..., min_length=1, max_length=255, description="Example title")
    description: Optional[str] = Field(None, description="Example description")
    status: str = Field("active", description="Example status")


class ExampleCreate(ExampleBase):
    """Schema for creating an example.
    
    Used for POST requests.
    """
    pass


class ExampleUpdate(BaseModel):
    """Schema for updating an example.
    
    Used for PUT/PATCH requests.
    All fields are optional for partial updates.
    """
    
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None


class ExampleResponse(ExampleBase):
    """Schema for example responses.
    
    Used for GET requests.
    Includes database fields like id and timestamps.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime
