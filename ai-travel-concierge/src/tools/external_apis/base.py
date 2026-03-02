"""
Base class for all external API tools.

This module provides a common foundation for all travel API wrappers with
integrated caching, rate limiting, error handling, and response normalization.
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel, Field
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun

from src.utils.cache_manager import CacheManager, CACHE_TTL
from src.utils.rate_limiter import get_rate_limiter


class APIResponse(BaseModel):
    """Standardized API response format."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    source: str
    cached: bool = False
    
    class Config:
        arbitrary_types_allowed = True


class BaseTravelAPITool(BaseTool, ABC):
    """
    Base class for all travel API tools.
    
    Features:
    - Integrated caching with configurable TTL
    - Rate limiting with automatic backoff
    - Standardized error handling
    - Response normalization
    - LangSmith tracing support
    """
    
    # These should be set by subclasses
    api_name: str = "unknown"
    cache_prefix: str = "api"
    
    # Cache and rate limiter (class-level, shared across instances)
    _cache_manager: Optional[CacheManager] = None
    _rate_limiter = get_rate_limiter()
    
    # HTTP client settings
    timeout: int = 30
    max_retries: int = 3
    
    def __init__(self, cache_manager: Optional[CacheManager] = None, **kwargs):
        """
        Initialize base API tool.
        
        Args:
            cache_manager: Shared cache manager instance
            **kwargs: Additional arguments for BaseTool
        """
        super().__init__(**kwargs)
        if cache_manager:
            self.__class__._cache_manager = cache_manager
    
    @classmethod
    def set_cache_manager(cls, cache_manager: CacheManager):
        """Set the shared cache manager for all instances."""
        cls._cache_manager = cache_manager
    
    def _get_cache_key(self, **params) -> str:
        """
        Generate cache key from parameters.
        
        Args:
            **params: Parameters to include in cache key
        
        Returns:
            Cache key string
        """
        key_parts = [self.cache_prefix]
        for k, v in sorted(params.items()):
            key_parts.append(f"{k}:{v}")
        return ":".join(key_parts)
    
    def _get_cache_ttl(self) -> int:
        """Get cache TTL for this tool type."""
        return CACHE_TTL.get(self.cache_prefix, 3600)
    
    async def _check_cache(self, **params) -> Optional[Dict[str, Any]]:
        """
        Check cache for existing result.
        
        Args:
            **params: Query parameters
        
        Returns:
            Cached result or None
        """
        if not self._cache_manager:
            return None
        
        cache_key = self._get_cache_key(**params)
        cached_data = await self._cache_manager.get(cache_key)
        
        if cached_data:
            return {
                "success": True,
                "data": cached_data,
                "source": self.api_name,
                "cached": True,
            }
        
        return None
    
    async def _save_cache(self, data: Dict[str, Any], **params) -> None:
        """
        Save result to cache.
        
        Args:
            data: Data to cache
            **params: Query parameters for key generation
        """
        if not self._cache_manager:
            return
        
        cache_key = self._get_cache_key(**params)
        ttl = self._get_cache_ttl()
        await self._cache_manager.set(cache_key, data, ttl=ttl)
    
    async def _acquire_rate_limit(self) -> bool:
        """
        Acquire rate limit permission.
        
        Returns:
            True if permission acquired
        
        Raises:
            ValueError: If daily quota exceeded
            TimeoutError: If max retries exceeded
        """
        return await self._rate_limiter.acquire_with_retry(
            self.api_name,
            max_retries=self.max_retries,
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
    )
    async def _make_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional arguments for httpx
        
        Returns:
            HTTP response
        
        Raises:
            httpx.HTTPStatusError: For HTTP errors
            httpx.TimeoutException: For timeouts
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
    
    def _handle_error(self, error: Exception) -> APIResponse:
        """
        Handle errors and return standardized response.
        
        Args:
            error: Exception that occurred
        
        Returns:
            APIResponse with error details
        """
        error_message = str(error)
        
        if isinstance(error, httpx.HTTPStatusError):
            status_code = error.response.status_code
            if status_code == 429:
                error_message = f"Rate limit exceeded for {self.api_name}"
            elif status_code == 401 or status_code == 403:
                error_message = f"Authentication failed for {self.api_name}"
            elif status_code == 404:
                error_message = "Resource not found"
            else:
                error_message = f"HTTP error {status_code}: {error.response.text[:200]}"
        elif isinstance(error, httpx.TimeoutException):
            error_message = f"Request timeout for {self.api_name}"
        elif isinstance(error, ValueError):
            # Rate limit or validation error
            error_message = str(error)
        
        return APIResponse(
            success=False,
            error=error_message,
            source=self.api_name,
            cached=False,
        )
    
    @abstractmethod
    async def _call_api(self, **params) -> Dict[str, Any]:
        """
        Call the external API (to be implemented by subclasses).
        
        Args:
            **params: API-specific parameters
        
        Returns:
            Raw API response data
        
        Raises:
            Exception: Any API errors
        """
        pass
    
    @abstractmethod
    def _normalize_response(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize API response to standard format (to be implemented by subclasses).
        
        Args:
            raw_data: Raw API response
        
        Returns:
            Normalized response data
        """
        pass
    
    async def execute(self, **params) -> APIResponse:
        """
        Execute API call with caching and rate limiting.
        
        Args:
            **params: API-specific parameters
        
        Returns:
            Standardized API response
        """
        try:
            # Check cache first
            cached_result = await self._check_cache(**params)
            if cached_result:
                return APIResponse(**cached_result)
            
            # Acquire rate limit
            await self._acquire_rate_limit()
            
            # Call API
            raw_data = await self._call_api(**params)
            
            # Normalize response
            normalized_data = self._normalize_response(raw_data)
            
            # Cache the result
            await self._save_cache(normalized_data, **params)
            
            return APIResponse(
                success=True,
                data=normalized_data,
                source=self.api_name,
                cached=False,
            )
        
        except Exception as e:
            return self._handle_error(e)
    
    def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **params
    ) -> Dict[str, Any]:
        """
        Synchronous run method (required by BaseTool).
        Uses asyncio to run async execute method.
        """
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If already in async context, create new loop
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.execute(**params))
                result = future.result()
        else:
            result = loop.run_until_complete(self.execute(**params))
        
        return result.model_dump()
    
    async def _arun(
        self,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
        **params
    ) -> Dict[str, Any]:
        """
        Asynchronous run method (required by BaseTool).
        """
        result = await self.execute(**params)
        return result.model_dump()
