"""Example endpoints.

Demonstrates CRUD operations with authentication.
Replace with your actual business logic endpoints.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import CurrentUser, get_current_user
from app.schemas.example import ExampleCreate, ExampleResponse, ExampleUpdate
from app.services.example_service import ExampleService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=List[ExampleResponse],
    summary="List examples",
    description="Get a list of examples with optional filtering and pagination",
)
async def list_examples(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """List all examples.
    
    This endpoint is protected and requires authentication.
    """
    logger.info(f"User {current_user.user_id} listing examples")
    
    service = ExampleService(db)
    examples = await service.get_all(
        skip=skip,
        limit=limit,
        status=status_filter,
    )
    
    return examples


@router.get(
    "/{example_id}",
    response_model=ExampleResponse,
    summary="Get example",
    description="Get a specific example by ID",
)
async def get_example(
    example_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get an example by ID."""
    logger.info(f"User {current_user.user_id} getting example {example_id}")
    
    service = ExampleService(db)
    example = await service.get(example_id)
    
    if not example:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Example with id {example_id} not found",
        )
    
    return example


@router.post(
    "/",
    response_model=ExampleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create example",
    description="Create a new example",
)
async def create_example(
    example_data: ExampleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Create a new example."""
    logger.info(f"User {current_user.user_id} creating example")
    
    service = ExampleService(db)
    example = await service.create(example_data)
    
    return example


@router.put(
    "/{example_id}",
    response_model=ExampleResponse,
    summary="Update example",
    description="Update an existing example",
)
async def update_example(
    example_id: int,
    example_data: ExampleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Update an example."""
    logger.info(f"User {current_user.user_id} updating example {example_id}")
    
    service = ExampleService(db)
    example = await service.update(example_id, example_data)
    
    if not example:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Example with id {example_id} not found",
        )
    
    return example


@router.delete(
    "/{example_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete example",
    description="Delete an example",
)
async def delete_example(
    example_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Delete an example."""
    logger.info(f"User {current_user.user_id} deleting example {example_id}")
    
    service = ExampleService(db)
    deleted = await service.delete(example_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Example with id {example_id} not found",
        )
    
    return None
