"""
Country information API tool using REST Countries (no authentication required).

REST Countries provides comprehensive country data with no API key needed.
Free tier: Unlimited calls, 250+ countries.
"""
from typing import Dict, Any, Optional, List, ClassVar
from pydantic import BaseModel, Field

from .base import BaseTravelAPITool


class CountryInput(BaseModel):
    """Input schema for country info tool."""
    query: str = Field(description="Country name, code (ISO 2/3), or capital city")
    search_by: str = Field(default="name", description="Search type: name, code, capital, or currency")


class CountryInfoTool(BaseTravelAPITool):
    """
    Get detailed country information using REST Countries API.
    
    Features:
    - No API key required
    - Comprehensive country data
    - Search by name, code, or capital
    - Currency, language, timezone info
    """
    
    name: str = "country_info"
    description: str = """Get detailed information about a country.
    Input should be country name (e.g., 'Japan'), ISO code (e.g., 'JP'), or capital city (e.g., 'Tokyo').
    Returns currency, languages, timezone, capital, population, flag, and more."""
    
    args_schema: type[BaseModel] = CountryInput
    
    api_name: str = "rest_countries"
    cache_prefix: str = "country"
    
    BASE_URL: ClassVar[str] = "https://restcountries.com/v3.1"
    
    async def _call_api(self, **params) -> Dict[str, Any]:
        """
        Call REST Countries API.
        
        Args:
            query: Search query (name, code, or capital)
            search_by: Type of search
        
        Returns:
            Raw API response
        """
        query = params.get("query", "")
        search_by = params.get("search_by", "name").lower()
        
        if not query:
            raise ValueError("Query parameter is required")
        
        # Build endpoint based on search type
        if search_by == "code":
            endpoint = f"{self.BASE_URL}/alpha/{query}"
        elif search_by == "capital":
            endpoint = f"{self.BASE_URL}/capital/{query}"
        elif search_by == "currency":
            endpoint = f"{self.BASE_URL}/currency/{query}"
        else:  # default to name search
            endpoint = f"{self.BASE_URL}/name/{query}"
        
        # Request with all fields
        params_dict = {"fullText": "false"}
        
        response = await self._make_request("GET", endpoint, params=params_dict)
        data = response.json()
        
        # API returns list, take first result
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        elif isinstance(data, dict):
            return data
        else:
            raise ValueError(f"No country found for query: {query}")
    
    def _normalize_response(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize REST Countries response to standard format.
        
        Args:
            raw_data: Raw API response
        
        Returns:
            Normalized country data
        """
        # Extract common name
        name_data = raw_data.get("name", {})
        common_name = name_data.get("common", "Unknown")
        official_name = name_data.get("official", common_name)
        
        # Extract currencies
        currencies_data = raw_data.get("currencies", {})
        currencies = []
        for code, info in currencies_data.items():
            currencies.append({
                "code": code,
                "name": info.get("name", ""),
                "symbol": info.get("symbol", ""),
            })
        
        # Extract languages
        languages_data = raw_data.get("languages", {})
        languages = list(languages_data.values())
        
        # Extract capital(s)
        capitals = raw_data.get("capital", [])
        
        # Extract timezone(s)
        timezones = raw_data.get("timezones", [])
        
        # Extract region info
        region = raw_data.get("region", "")
        subregion = raw_data.get("subregion", "")
        
        # Extract flag
        flags = raw_data.get("flags", {})
        flag_url = flags.get("png", flags.get("svg", ""))
        
        # Extract coat of arms
        coat_of_arms = raw_data.get("coatOfArms", {})
        coat_url = coat_of_arms.get("png", coat_of_arms.get("svg", ""))
        
        # Extract codes
        cca2 = raw_data.get("cca2", "")  # ISO 3166-1 alpha-2
        cca3 = raw_data.get("cca3", "")  # ISO 3166-1 alpha-3
        
        # Extract population and area
        population = raw_data.get("population", 0)
        area = raw_data.get("area", 0)
        
        # Extract borders
        borders = raw_data.get("borders", [])
        
        # Extract driving side
        car_info = raw_data.get("car", {})
        driving_side = car_info.get("side", "unknown")
        
        # Extract maps
        maps = raw_data.get("maps", {})
        google_maps = maps.get("googleMaps", "")
        
        # Extract demonyms (what people from the country are called)
        demonyms = raw_data.get("demonyms", {}).get("eng", {})
        demonym = demonyms.get("m", "")  # masculine form
        
        return {
            "name": {
                "common": common_name,
                "official": official_name,
            },
            "codes": {
                "iso_alpha_2": cca2,
                "iso_alpha_3": cca3,
            },
            "capital": capitals[0] if capitals else None,
            "all_capitals": capitals,
            "region": region,
            "subregion": subregion,
            "currencies": currencies,
            "primary_currency": currencies[0] if currencies else None,
            "languages": languages,
            "population": population,
            "area_km2": area,
            "timezones": timezones,
            "timezone": timezones[0] if timezones else None,
            "borders": borders,
            "driving_side": driving_side,
            "demonym": demonym,
            "flag_url": flag_url,
            "coat_of_arms_url": coat_url,
            "google_maps_url": google_maps,
        }
