"""
Weather API tool using Open-Meteo (no authentication required).

Open-Meteo provides free weather forecasts with no API key needed.
Free tier: 10,000 calls/day, 16-day forecast.
"""
from typing import Dict, Any, Optional, ClassVar
from pydantic import BaseModel, Field

from .base import BaseTravelAPITool


class WeatherInput(BaseModel):
    """Input schema for weather forecast tool."""
    location: str = Field(description="Location name (city, country) or coordinates (lat,lon)")
    days: int = Field(default=7, description="Number of forecast days (1-16)")
    units: str = Field(default="celsius", description="Temperature units: celsius or fahrenheit")


class WeatherForecastTool(BaseTravelAPITool):
    """
    Get weather forecast for a location using Open-Meteo API.
    
    Features:
    - No API key required
    - Up to 16-day forecast  
    - Temperature, precipitation, wind, etc.
    - Automatic geocoding for location names
    """
    
    name: str = "weather_forecast"
    description: str = """Get weather forecast for a location. 
    Input should be a location name (e.g., 'Paris, France') or coordinates.
    Returns temperature, conditions, precipitation for up to 16 days."""
    
    args_schema: type[BaseModel] = WeatherInput
    
    api_name: str = "open_meteo"
    cache_prefix: str = "weather"
    
    GEOCODING_URL: ClassVar[str] = "https://geocoding-api.open-meteo.com/v1/search"
    FORECAST_URL: ClassVar[str] = "https://api.open-meteo.com/v1/forecast"
    
    WEATHER_CODES: ClassVar[dict] = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }
    
    async def _geocode_location(self, location: str) -> tuple[float, float, str]:
        """
        Convert location name to coordinates.
        
        Args:
            location: Location name
        
        Returns:
            Tuple of (latitude, longitude, formatted_name)
        
        Raises:
            ValueError: If location not found
        """
        # Check if already coordinates (lat,lon format)
        if ',' in location and all(part.replace('.', '').replace('-', '').strip().isdigit() 
                                  for part in location.split(',')):
            lat_str, lon_str = location.split(',')
            return float(lat_str.strip()), float(lon_str.strip()), location
        
        # Geocode location name
        response = await self._make_request(
            "GET",
            self.GEOCODING_URL,
            params={"name": location, "count": 1, "language": "en", "format": "json"}
        )
        
        data = response.json()
        
        if not data.get("results"):
            raise ValueError(f"Location '{location}' not found")
        
        result = data["results"][0]
        return result["latitude"], result["longitude"], f"{result['name']}, {result.get('country', '')}"
    
    async def _call_api(self, **params) -> Dict[str, Any]:
        """
        Call Open-Meteo API.
        
        Args:
            location: Location name or coordinates
            days: Number of forecast days
            units: Temperature units
        
        Returns:
            Raw API response
        """
        location = params.get("location", "")
        days = min(params.get("days", 7), 16)  # Cap at 16 days
        units = params.get("units", "celsius")
        
        # Get coordinates
        latitude, longitude, formatted_location = await self._geocode_location(location)
        
        # Prepare API parameters
        temperature_unit = "fahrenheit" if units.lower() == "fahrenheit" else "celsius"
        
        api_params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,windspeed_10m_max",
            "current_weather": "true",
            "temperature_unit": temperature_unit,
            "windspeed_unit": "kmh",
            "precipitation_unit": "mm",
            "timezone": "auto",
            "forecast_days": days,
        }
        
        response = await self._make_request("GET", self.FORECAST_URL, params=api_params)
        data = response.json()
        data["_formatted_location"] = formatted_location
        
        return data
    
    def _normalize_response(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Open-Meteo response to standard format.
        
        Args:
            raw_data: Raw API response
        
        Returns:
            Normalized weather data
        """
        current = raw_data.get("current_weather", {})
        daily = raw_data.get("daily", {})
        
        # Build forecast list
        forecast = []
        for i in range(len(daily.get("time", []))):
            weather_code = daily["weathercode"][i]
            forecast.append({
                "date": daily["time"][i],
                "high": daily["temperature_2m_max"][i],
                "low": daily["temperature_2m_min"][i],
                "condition": self.WEATHER_CODES.get(weather_code, "Unknown"),
                "weather_code": weather_code,
                "precipitation_mm": daily["precipitation_sum"][i],
                "max_wind_kmh": daily["windspeed_10m_max"][i],
            })
        
        return {
            "location": raw_data.get("_formatted_location", "Unknown Location"),
            "latitude": raw_data.get("latitude"),
            "longitude": raw_data.get("longitude"),
            "timezone": raw_data.get("timezone"),
            "current": {
                "temperature": current.get("temperature"),
                "windspeed": current.get("windspeed"),
                "wind_direction": current.get("winddirection"),
                "weather_code": current.get("weathercode"),
                "condition": self.WEATHER_CODES.get(current.get("weathercode", 0), "Unknown"),
                "time": current.get("time"),
            },
            "forecast": forecast,
            "unit": raw_data.get("daily_units", {}).get("temperature_2m_max", "°C"),
        }
