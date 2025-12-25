"""Auth Service - JWT validation and user context"""
from typing import Optional, Dict, Any
from uuid import UUID
import httpx
from jose import jwt, JWTError

from app.core.config import settings


class AuthService:
    """Service for authentication and authorization"""
    
    def __init__(self):
        self.auth_service_url = settings.AUTH_SERVICE_URL
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token via Auth Service
        
        Args:
            token: JWT token
            
        Returns:
            User context dict or None if invalid
        """
        try:
            # Try to decode token locally first (faster)
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
            
        except JWTError:
            # If local validation fails, try remote validation
            try:
                response = await self.client.get(
                    f"{self.auth_service_url}/api/v1/auth/validate",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    return response.json()
                
            except httpx.HTTPError:
                pass
        
        return None
    
    def extract_token(self, authorization: Optional[str]) -> Optional[str]:
        """Extract token from Authorization header
        
        Args:
            authorization: Authorization header value
            
        Returns:
            Token string or None
        """
        if not authorization:
            return None
        
        if authorization.startswith('Bearer '):
            return authorization[7:]
        
        return None
    
    async def get_user_context(self, authorization: Optional[str]) -> Optional[Dict[str, Any]]:
        """Get user context from authorization header
        
        Args:
            authorization: Authorization header value
            
        Returns:
            User context dict or None
        """
        token = self.extract_token(authorization)
        if not token:
            return None
        
        return await self.validate_token(token)
    
    async def get_user_id(self, authorization: Optional[str]) -> Optional[UUID]:
        """Extract user ID from authorization header
        
        Args:
            authorization: Authorization header value
            
        Returns:
            User ID or None
        """
        context = await self.get_user_context(authorization)
        if context and 'user_id' in context:
            return UUID(context['user_id'])
        return None
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
