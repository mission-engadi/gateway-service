"""Example service for business logic.

Services encapsulate business logic and database operations.
They provide a clean separation between API endpoints and data access.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.example import ExampleModel
from app.schemas.example import ExampleCreate, ExampleUpdate


class ExampleService:
    """Service for managing examples.
    
    This service demonstrates common CRUD operations.
    Adapt it to your specific business logic needs.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize service with database session."""
        self.db = db
    
    async def get(self, example_id: int) -> Optional[ExampleModel]:
        """Get an example by ID."""
        result = await self.db.execute(
            select(ExampleModel).where(ExampleModel.id == example_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> list[ExampleModel]:
        """Get all examples with optional filtering and pagination."""
        query = select(ExampleModel)
        
        # Apply filters
        if status:
            query = query.where(ExampleModel.status == status)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def create(self, example_data: ExampleCreate) -> ExampleModel:
        """Create a new example."""
        example = ExampleModel(**example_data.model_dump())
        self.db.add(example)
        await self.db.flush()
        await self.db.refresh(example)
        return example
    
    async def update(
        self,
        example_id: int,
        example_data: ExampleUpdate,
    ) -> Optional[ExampleModel]:
        """Update an existing example."""
        example = await self.get(example_id)
        
        if not example:
            return None
        
        # Update only provided fields
        update_data = example_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(example, field, value)
        
        await self.db.flush()
        await self.db.refresh(example)
        return example
    
    async def delete(self, example_id: int) -> bool:
        """Delete an example."""
        example = await self.get(example_id)
        
        if not example:
            return False
        
        await self.db.delete(example)
        await self.db.flush()
        return True
