"""Rate Limit Service - Rate limiting logic"""
from datetime import datetime, timedelta
from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.rate_limit_rule import RateLimitRule, LimitType
from app.schemas.rate_limit_rule import RateLimitRuleCreate, RateLimitRuleUpdate, RateLimitStatus


class RateLimitService:
    """Service for rate limiting"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        # In-memory cache for rate limiting (use Redis in production)
        self._rate_limit_cache: Dict[str, Dict] = {}
    
    async def check_rate_limit(
        self,
        path: str,
        user_id: Optional[UUID] = None,
        client_ip: Optional[str] = None
    ) -> tuple[bool, Optional[RateLimitStatus]]:
        """Check if request is within rate limits
        
        Args:
            path: Request path
            user_id: User ID (if authenticated)
            client_ip: Client IP address
            
        Returns:
            Tuple of (is_allowed, rate_limit_status)
        """
        # Get applicable rate limit rules
        rules = await self._get_applicable_rules(path)
        
        for rule in rules:
            # Determine key based on limit type
            key = self._get_rate_limit_key(rule, user_id, client_ip, path)
            
            # Check limit
            is_allowed, status = self._check_limit(key, rule)
            
            if not is_allowed:
                return False, status
        
        return True, None
    
    async def _get_applicable_rules(self, path: str) -> list[RateLimitRule]:
        """Get rate limit rules applicable to a path"""
        stmt = select(RateLimitRule).where(
            RateLimitRule.is_active == True
        )
        
        result = await self.db.execute(stmt)
        rules = result.scalars().all()
        
        # Filter rules that match the path
        applicable = []
        for rule in rules:
            if rule.path_pattern is None or path.startswith(rule.path_pattern):
                applicable.append(rule)
        
        return applicable
    
    def _get_rate_limit_key(
        self,
        rule: RateLimitRule,
        user_id: Optional[UUID],
        client_ip: Optional[str],
        path: str
    ) -> str:
        """Generate rate limit key based on rule type"""
        if rule.limit_type == LimitType.PER_USER and user_id:
            return f"user:{user_id}:{rule.id}"
        elif rule.limit_type == LimitType.PER_IP and client_ip:
            return f"ip:{client_ip}:{rule.id}"
        elif rule.limit_type == LimitType.PER_ENDPOINT:
            return f"endpoint:{path}:{rule.id}"
        else:  # GLOBAL
            return f"global:{rule.id}"
    
    def _check_limit(self, key: str, rule: RateLimitRule) -> tuple[bool, Optional[RateLimitStatus]]:
        """Check if key is within rate limit"""
        now = datetime.utcnow()
        
        # Initialize or get existing cache entry
        if key not in self._rate_limit_cache:
            self._rate_limit_cache[key] = {
                'count': 0,
                'window_start': now
            }
        
        cache_entry = self._rate_limit_cache[key]
        
        # Check if window has expired
        window_end = cache_entry['window_start'] + timedelta(seconds=rule.window_seconds)
        if now > window_end:
            # Reset window
            cache_entry['count'] = 0
            cache_entry['window_start'] = now
        
        # Check limit
        current_count = cache_entry['count']
        if current_count >= rule.max_requests:
            # Limit exceeded
            status = RateLimitStatus(
                key=key,
                limit_type=rule.limit_type,
                current_requests=current_count,
                max_requests=rule.max_requests,
                window_seconds=rule.window_seconds,
                remaining=0,
                reset_at=window_end
            )
            return False, status
        
        # Increment count
        cache_entry['count'] += 1
        
        status = RateLimitStatus(
            key=key,
            limit_type=rule.limit_type,
            current_requests=cache_entry['count'],
            max_requests=rule.max_requests,
            window_seconds=rule.window_seconds,
            remaining=rule.max_requests - cache_entry['count'],
            reset_at=window_end
        )
        
        return True, status
    
    async def get_rate_limit_rules(self) -> list[RateLimitRule]:
        """Get all rate limit rules"""
        stmt = select(RateLimitRule)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def create_rule(self, rule_data: RateLimitRuleCreate) -> RateLimitRule:
        """Create new rate limit rule"""
        rule = RateLimitRule(**rule_data.model_dump())
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        return rule
    
    async def update_rule(self, rule_id: str, rule_data: RateLimitRuleUpdate) -> Optional[RateLimitRule]:
        """Update rate limit rule"""
        stmt = select(RateLimitRule).where(RateLimitRule.id == rule_id)
        result = await self.db.execute(stmt)
        rule = result.scalar_one_or_none()
        
        if not rule:
            return None
        
        for field, value in rule_data.model_dump(exclude_unset=True).items():
            setattr(rule, field, value)
        
        await self.db.commit()
        await self.db.refresh(rule)
        return rule
    
    async def delete_rule(self, rule_id: str) -> bool:
        """Delete rate limit rule"""
        stmt = select(RateLimitRule).where(RateLimitRule.id == rule_id)
        result = await self.db.execute(stmt)
        rule = result.scalar_one_or_none()
        
        if not rule:
            return False
        
        await self.db.delete(rule)
        await self.db.commit()
        return True
