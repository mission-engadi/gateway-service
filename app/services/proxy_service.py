"""Proxy Service - Forward requests to target services"""
import asyncio
import time
from typing import Any, Dict, Optional
import httpx
from uuid import UUID

from app.schemas.proxy import ProxyRequest, ProxyResponse, GatewayError


class ProxyService:
    """Service for proxying requests to downstream services"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def forward_request(
        self,
        target_url: str,
        method: str,
        path: str,
        headers: Dict[str, str],
        query_params: Optional[Dict[str, Any]] = None,
        body: Optional[Any] = None,
        user_id: Optional[UUID] = None,
        request_id: Optional[UUID] = None,
        timeout: int = 30,
        retry_count: int = 3
    ) -> ProxyResponse:
        """Forward request to target service
        
        Args:
            target_url: Target service base URL
            method: HTTP method
            path: Request path
            headers: Request headers
            query_params: Query parameters
            body: Request body
            user_id: Authenticated user ID
            request_id: Request tracking ID
            timeout: Request timeout in seconds
            retry_count: Number of retry attempts
            
        Returns:
            ProxyResponse
            
        Raises:
            httpx.HTTPError: On request failure
        """
        # Build full URL
        full_url = f"{target_url.rstrip('/')}{path}"
        
        # Add custom headers
        forward_headers = headers.copy()
        if user_id:
            forward_headers['X-User-ID'] = str(user_id)
        if request_id:
            forward_headers['X-Request-ID'] = str(request_id)
        forward_headers['X-Forwarded-By'] = 'Mission-Engadi-Gateway'
        
        # Remove host header to avoid conflicts
        forward_headers.pop('host', None)
        forward_headers.pop('Host', None)
        
        start_time = time.time()
        
        # Retry logic
        last_exception = None
        for attempt in range(retry_count):
            try:
                response = await self.client.request(
                    method=method,
                    url=full_url,
                    headers=forward_headers,
                    params=query_params,
                    json=body if body else None,
                    timeout=timeout
                )
                
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                # Extract service name from URL
                target_service = target_url.split('//')[-1].split(':')[0]
                
                return ProxyResponse(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    body=response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                    response_time=response_time,
                    target_service=target_service
                )
                
            except httpx.TimeoutException as e:
                last_exception = e
                if attempt < retry_count - 1:
                    await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                continue
                
            except httpx.HTTPError as e:
                last_exception = e
                if attempt < retry_count - 1:
                    await asyncio.sleep(0.5 * (attempt + 1))
                continue
        
        # All retries failed
        response_time = (time.time() - start_time) * 1000
        raise last_exception
    
    async def health_check(self, service_url: str, timeout: int = 5) -> tuple[bool, float]:
        """Check health of a service
        
        Args:
            service_url: Service URL
            timeout: Health check timeout
            
        Returns:
            Tuple of (is_healthy, response_time_ms)
        """
        try:
            start_time = time.time()
            health_url = f"{service_url.rstrip('/')}/health"
            
            response = await self.client.get(health_url, timeout=timeout)
            response_time = (time.time() - start_time) * 1000
            
            return response.status_code == 200, response_time
            
        except Exception:
            response_time = (time.time() - start_time) * 1000
            return False, response_time
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
