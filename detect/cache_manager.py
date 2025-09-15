"""
Cache Manager for FastAPI Performance Optimization
Implements in-memory caching with TTL and LRU eviction
"""
import time
import asyncio
from typing import Dict, Any, Optional, Callable
from functools import wraps
import json
import hashlib

class CacheManager:
    def __init__(self, default_ttl: int = 300):  # 5 minutes default TTL
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self.max_size = 1000  # Maximum cache entries
        
    def _get_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a unique cache key from function arguments"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        if key in self._cache:
            entry = self._cache[key]
            if time.time() < entry['expires_at']:
                entry['last_accessed'] = time.time()  # Update LRU
                return entry['value']
            else:
                # Expired, remove from cache
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cached value with TTL"""
        if ttl is None:
            ttl = self.default_ttl
            
        # Implement simple LRU eviction if cache is full
        if len(self._cache) >= self.max_size:
            self._evict_lru()
        
        self._cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl,
            'last_accessed': time.time()
        }
    
    def _evict_lru(self) -> None:
        """Remove least recently used entry"""
        if not self._cache:
            return
            
        lru_key = min(self._cache.keys(), 
                     key=lambda k: self._cache[k]['last_accessed'])
        del self._cache[lru_key]
    
    def invalidate(self, pattern: str = None) -> None:
        """Invalidate cache entries matching pattern"""
        if pattern is None:
            self._cache.clear()
        else:
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self._cache[key]
    
    def cache_response(self, prefix: str, ttl: int = None):
        """Decorator for caching async function responses"""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                cache_key = self._get_cache_key(prefix, *args, **kwargs)
                
                # Try to get from cache first
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                return result
            return wrapper
        return decorator

# Global cache instance
cache_manager = CacheManager()

def cached_query(prefix: str, ttl: int = 300):
    """Decorator for caching database queries"""
    return cache_manager.cache_response(prefix, ttl)