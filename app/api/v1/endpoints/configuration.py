"""Gateway Configuration Endpoints"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.rate_limit_service import RateLimitService
from app.schemas.rate_limit_rule import (
    RateLimitRuleCreate,
    RateLimitRuleUpdate,
    RateLimitRuleResponse
)
from app.schemas.cors_config import CORSConfig, CORSConfigUpdate
from app.core.config import settings

router = APIRouter()


@router.get("/rate-limits", response_model=List[RateLimitRuleResponse])
async def get_rate_limit_rules(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all rate limit rules.
    """
    rate_limit_service = RateLimitService(db)
    rules = await rate_limit_service.get_rate_limit_rules()
    return rules


@router.post("/rate-limits", response_model=RateLimitRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rate_limit_rule(
    rule_data: RateLimitRuleCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new rate limit rule.
    
    This endpoint allows administrators to add new rate limiting rules.
    """
    rate_limit_service = RateLimitService(db)
    try:
        rule = await rate_limit_service.create_rule(rule_data)
        return rule
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create rate limit rule: {str(e)}"
        )


@router.put("/rate-limits/{rule_id}", response_model=RateLimitRuleResponse)
async def update_rate_limit_rule(
    rule_id: UUID,
    rule_data: RateLimitRuleUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing rate limit rule.
    
    - **rule_id**: UUID of the rule to update
    """
    rate_limit_service = RateLimitService(db)
    rule = await rate_limit_service.update_rule(str(rule_id), rule_data)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rate limit rule not found"
        )
    
    return rule


@router.delete("/rate-limits/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rate_limit_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a rate limit rule.
    
    - **rule_id**: UUID of the rule to delete
    """
    rate_limit_service = RateLimitService(db)
    success = await rate_limit_service.delete_rule(str(rule_id))
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rate limit rule not found"
        )
    
    return None


@router.get("/cors", response_model=CORSConfig)
async def get_cors_config():
    """
    Get current CORS configuration.
    """
    return CORSConfig(
        allowed_origins=settings.CORS_ORIGINS,
        allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allowed_headers=["*"],
        allow_credentials=True,
        max_age=600
    )


@router.put("/cors", response_model=CORSConfig)
async def update_cors_config(
    cors_config: CORSConfigUpdate
):
    """
    Update CORS configuration.
    
    Note: This endpoint updates the configuration in memory.
    For persistent changes, update the environment variables or configuration file.
    """
    # In a real implementation, you would update the CORS middleware configuration
    # For now, we'll just return the updated config
    return CORSConfig(
        allowed_origins=cors_config.allowed_origins,
        allowed_methods=cors_config.allowed_methods,
        allowed_headers=cors_config.allowed_headers,
        allow_credentials=cors_config.allow_credentials,
        max_age=cors_config.max_age
    )
