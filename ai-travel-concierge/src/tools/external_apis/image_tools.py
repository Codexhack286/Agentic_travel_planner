"""
Unsplash API tool for fetching high-quality destination images.

Unsplash provides free, high-quality stock photos.
Free tier: 50 requests/hour per application.
API Docs: https://unsplash.com/documentation
"""
import os
from typing import Dict, Any, Optional, ClassVar, List
from pydantic import BaseModel, Field
from pydantic import PrivateAttr

from .base import BaseTravelAPITool


class UnsplashImageInput(BaseModel):
    """Input schema for Unsplash image search tool."""
    query: str = Field(description="Search query for images (e.g., 'Paris Eiffel Tower', 'Tokyo skyline')")
    per_page: int = Field(default=5, description="Number of images to return (1-30)", ge=1, le=30)
    orientation: Optional[str] = Field(default=None, description="Image orientation: landscape, portrait, or squarish")


class UnsplashImageTool(BaseTravelAPITool):
    """
    Search for high-quality destination photos using Unsplash API.
    
    Features:
    - High-quality, professional photos
    - Free tier: 50 requests/hour
    - Automatic attribution info included
    - Filter by orientation
    
    Setup:
    1. Create account at https://unsplash.com/developers
    2. Create a new application
    3. Copy your Access Key
    4. Add to .env: UNSPLASH_ACCESS_KEY=your_key_here
    
    LangGraph Integration:
    This tool is fully compatible with LangGraph nodes and can be used
    in multi-agent workflows. It supports async execution and proper
    LangSmith tracing through the BaseTravelAPITool infrastructure.
    """
    
    name: str = "search_destination_images"
    description: str = """Search for high-quality destination photos from Unsplash.
    Input should be a location or landmark (e.g., 'Paris Eiffel Tower', 'Bali beaches').
    Returns image URLs with photographer attribution and licensing info.
    Use this to show users beautiful photos of destinations they're planning to visit."""
    
    args_schema: type[BaseModel] = UnsplashImageInput
    
    api_name: str = "unsplash"
    cache_prefix: str = "images"

    _access_key: str = PrivateAttr(default="")
    
    @property
    def access_key(self) -> str:
        return self._access_key
    
    BASE_URL: ClassVar[str] = "https://api.unsplash.com"
    
    def __init__(self, **kwargs):
        """Initialize Unsplash tool with API key from environment."""
        super().__init__(**kwargs)
        self._access_key = os.getenv("UNSPLASH_ACCESS_KEY")
        if not self._access_key:
            raise ValueError(
                "UNSPLASH_ACCESS_KEY not found in environment variables. "
                "Please sign up at https://unsplash.com/developers and add your key to .env"
            )
    
    async def _call_api(self, **params) -> Dict[str, Any]:
        """
        Call Unsplash Search API.
        
        Args:
            query: Search query
            per_page: Number of results (1-30)
            orientation: Optional orientation filter
        
        Returns:
            Raw API response
        
        Raises:
            ValueError: If query is empty
            httpx.HTTPStatusError: For API errors
        """
        query = params.get("query", "")
        per_page = min(params.get("per_page", 5), 30)
        orientation = params.get("orientation")
        
        if not query:
            raise ValueError("Search query is required")
        
        # Prepare API parameters
        api_params = {
            "query": query,
            "per_page": per_page,
        }
        
        if orientation and orientation in ["landscape", "portrait", "squarish"]:
            api_params["orientation"] = orientation
        
        # Make request with authorization header
        headers = {
            "Authorization": f"Client-ID {self._access_key}",
            "Accept-Version": "v1"
        }
        
        response = await self._make_request(
            "GET",
            f"{self.BASE_URL}/search/photos",
            params=api_params,
            headers=headers
        )
        
        return response.json()
    
    def _normalize_response(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Unsplash response to standard format.
        
        Args:
            raw_data: Raw API response from Unsplash
        
        Returns:
            Normalized image data with URLs and attribution.
            Includes all necessary data for LangGraph nodes to process
            and display images to users.
        """
        results = raw_data.get("results", [])
        total = raw_data.get("total", 0)
        
        # Extract essential image info
        images: List[Dict[str, Any]] = []
        for photo in results:
            images.append({
                "id": photo.get("id"),
                "description": photo.get("description") or photo.get("alt_description", ""),
                "urls": {
                    "raw": photo.get("urls", {}).get("raw"),
                    "full": photo.get("urls", {}).get("full"),
                    "regular": photo.get("urls", {}).get("regular"),  # Recommended for display
                    "small": photo.get("urls", {}).get("small"),
                    "thumb": photo.get("urls", {}).get("thumb"),
                },
                "width": photo.get("width"),
                "height": photo.get("height"),
                "color": photo.get("color"),
                # Attribution info (required by Unsplash API terms)
                "photographer": {
                    "name": photo.get("user", {}).get("name"),
                    "username": photo.get("user", {}).get("username"),
                    "profile_url": photo.get("user", {}).get("links", {}).get("html"),
                },
                "unsplash_url": photo.get("links", {}).get("html"),
                # Download tracking URL (call this when displaying the photo)
                "download_location": photo.get("links", {}).get("download_location"),
            })
        
        return {
            "total_results": total,
            "returned_count": len(images),
            "images": images,
            "attribution_required": True,
            "attribution_text": "Photos provided by Unsplash",
            "terms_url": "https://unsplash.com/license",
        }


# Utility function for LangGraph nodes to format attribution
def format_unsplash_attribution(image_data: Dict[str, Any]) -> str:
    """
    Format proper attribution text for an Unsplash image.
    
    Use this in your LangGraph nodes when displaying images to users.
    
    Args:
        image_data: Single image object from normalized response
    
    Returns:
        Formatted attribution string
    
    Example:
        >>> image = result['images'][0]
        >>> attribution = format_unsplash_attribution(image)
        >>> print(attribution)
        "Photo by John Doe on Unsplash"
    """
    photographer = image_data.get("photographer", {})
    name = photographer.get("name", "Unknown")
    return f"Photo by {name} on Unsplash"