"""Routing Service - Route matching and resolution"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fnmatch import fnmatch

from app.models.route_config import RouteConfig
from app.schemas.route_config import RouteConfigCreate, RouteConfigUpdate, RouteConfigResponse


class RoutingService:
    """Service for managing and matching routes"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def match_route(self, path: str, method: str) -> Optional[RouteConfig]:
        """Match incoming request to a route configuration
        
        Args:
            path: Request path
            method: HTTP method
            
        Returns:
            Matched RouteConfig or None
        """
        # Get all active routes ordered by priority (higher first)
        stmt = select(RouteConfig).where(
            RouteConfig.is_active == True
        ).order_by(RouteConfig.priority.desc())
        
        result = await self.db.execute(stmt)
        routes = result.scalars().all()
        
        # Match path pattern and method
        for route in routes:
            # Convert pattern to match (e.g., /api/v1/auth/* -> /api/v1/auth/**)
            pattern = route.path_pattern.replace('*', '**')
            if fnmatch(path, pattern) and method in route.methods:
                return route
        
        return None
    
    async def get_route_by_id(self, route_id: str) -> Optional[RouteConfig]:
        """Get route by ID"""
        stmt = select(RouteConfig).where(RouteConfig.id == route_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all_routes(self, active_only: bool = False) -> List[RouteConfig]:
        """Get all routes
        
        Args:
            active_only: If True, return only active routes
            
        Returns:
            List of RouteConfig
        """
        stmt = select(RouteConfig)
        if active_only:
            stmt = stmt.where(RouteConfig.is_active == True)
        stmt = stmt.order_by(RouteConfig.priority.desc())
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def create_route(self, route_data: RouteConfigCreate) -> RouteConfig:
        """Create a new route configuration"""
        route = RouteConfig(**route_data.model_dump())
        self.db.add(route)
        await self.db.commit()
        await self.db.refresh(route)
        return route
    
    async def update_route(self, route_id: str, route_data: RouteConfigUpdate) -> Optional[RouteConfig]:
        """Update route configuration"""
        route = await self.get_route_by_id(route_id)
        if not route:
            return None
        
        # Update fields
        for field, value in route_data.model_dump(exclude_unset=True).items():
            setattr(route, field, value)
        
        await self.db.commit()
        await self.db.refresh(route)
        return route
    
    async def delete_route(self, route_id: str) -> bool:
        """Delete route configuration"""
        route = await self.get_route_by_id(route_id)
        if not route:
            return False
        
        await self.db.delete(route)
        await self.db.commit()
        return True
    
    async def get_target_url(self, path: str, method: str) -> Optional[str]:
        """Get target service URL for a request
        
        Args:
            path: Request path
            method: HTTP method
            
        Returns:
            Target service URL or None
        """
        route = await self.match_route(path, method)
        if route:
            return route.target_url
        return None
    
    async def is_public_route(self, path: str, method: str) -> bool:
        """Check if route is public (doesn't require authentication)
        
        Args:
            path: Request path
            method: HTTP method
            
        Returns:
            True if route is public, False otherwise
        """
        route = await self.match_route(path, method)
        if route:
            return route.is_public
        return False
