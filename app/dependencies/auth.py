"""Authentication dependencies.

Provides dependency functions for protecting routes and extracting user context.
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.core.security import decode_token

# HTTP Bearer token security scheme
security = HTTPBearer()


class CurrentUser:
    """Current user context extracted from JWT token.
    
    This class represents the authenticated user making the request.
    Add additional fields as needed for your application.
    """
    
    def __init__(self, user_id: int, email: str, roles: list[str] = None):
        self.user_id = user_id
        self.email = email
        self.roles = roles or []
    
    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return role in self.roles
    
    def __repr__(self) -> str:
        return f"<CurrentUser(user_id={self.user_id}, email='{self.email}')>"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """Extract and validate current user from JWT token.
    
    This dependency can be used to protect routes and get user context.
    
    Usage:
        @router.get("/protected")
        async def protected_route(user: CurrentUser = Depends(get_current_user)):
            return {"user_id": user.user_id}
    
    Args:
        credentials: HTTP Bearer credentials from request header
    
    Returns:
        CurrentUser object with user information
    
    Raises:
        HTTPException: If token is invalid or missing
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        # Extract user information from token
        user_id: Optional[str] = payload.get("sub")
        email: Optional[str] = payload.get("email")
        roles: list[str] = payload.get("roles", [])
        
        if user_id is None:
            raise credentials_exception
        
        return CurrentUser(
            user_id=int(user_id),
            email=email or "",
            roles=roles,
        )
    
    except (JWTError, ValueError):
        raise credentials_exception


def require_auth(required_roles: list[str] = None):
    """Create a dependency that requires specific roles.
    
    This is a dependency factory that returns a dependency function.
    Use it to protect routes that require specific roles.
    
    Usage:
        @router.get("/admin")
        async def admin_route(
            user: CurrentUser = Depends(require_auth(["admin"]))
        ):
            return {"message": "Admin access granted"}
    
    Args:
        required_roles: List of roles required to access the route
    
    Returns:
        Dependency function that validates user roles
    """
    
    async def check_roles(
        user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        """Check if user has required roles."""
        if required_roles:
            if not any(user.has_role(role) for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )
        return user
    
    return check_roles
