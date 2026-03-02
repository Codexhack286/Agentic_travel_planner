"""
Amadeus API tools for flight and hotel searches.

Amadeus provides comprehensive travel data including flights, hotels, and more.
Test environment: 2,000-10,000 calls/month per endpoint (free).
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, PrivateAttr
from datetime import datetime, timedelta
import os

from .base import BaseTravelAPITool


class AmadeusAuthMixin:
    """Mixin for Amadeus OAuth2 authentication."""

    AMADEUS_AUTH_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
    AMADEUS_BASE_URL = "https://test.api.amadeus.com"

    async def _get_access_token(self) -> str:
        """Get or refresh Amadeus OAuth2 access token."""
        # Read token from __pydantic_private__ safely
        token = self.__pydantic_private__.get("_access_token")
        expiry = self.__pydantic_private__.get("_token_expiry")

        if token and expiry and datetime.now() < expiry:
            return token

        api_key = os.environ.get("AMADEUS_API_KEY")
        api_secret = os.environ.get("AMADEUS_API_SECRET")

        if not api_key or not api_secret:
            raise ValueError("Amadeus API credentials not found in environment variables")

        response = await self._make_request(
            "POST",
            self.AMADEUS_AUTH_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": api_key,
                "client_secret": api_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        token_data = response.json()
        new_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 1800) - 300
        new_expiry = datetime.now() + timedelta(seconds=expires_in)

        self.__pydantic_private__["_access_token"] = new_token
        self.__pydantic_private__["_token_expiry"] = new_expiry

        return new_token

    async def _make_amadeus_request(self, method: str, endpoint: str, **kwargs):
        """Make authenticated request to Amadeus API."""
        token = await self._get_access_token()

        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["Authorization"] = f"Bearer {token}"

        url = f"{self.AMADEUS_BASE_URL}{endpoint}"
        return await self._make_request(method, url, **kwargs)


class FlightSearchInput(BaseModel):
    """Input schema for flight search tool."""
    origin: str = Field(description="Origin airport code (IATA, e.g., NYC, LAX)")
    destination: str = Field(description="Destination airport code (IATA, e.g., LHR, CDG)")
    departure_date: str = Field(description="Departure date (YYYY-MM-DD)")
    return_date: Optional[str] = Field(default=None, description="Return date for round trip (YYYY-MM-DD)")
    adults: int = Field(default=1, description="Number of adult passengers (1-9)")
    travel_class: str = Field(default="ECONOMY", description="Travel class: ECONOMY, PREMIUM_ECONOMY, BUSINESS, or FIRST")
    max_results: int = Field(default=5, description="Maximum number of results (1-250)")


class FlightSearchTool(AmadeusAuthMixin, BaseTravelAPITool):
    """Search for flight offers using Amadeus API."""

    name: str = "flight_search"
    description: str = """Search for flight offers between cities.
    Input should include origin airport (e.g., 'JFK'), destination (e.g., 'LHR'),
    departure date (YYYY-MM-DD), and optionally return date for round trips.
    Returns flight options with prices, duration, and airline details."""

    args_schema: type[BaseModel] = FlightSearchInput

    api_name: str = "amadeus"
    cache_prefix: str = "flight"

    _access_token: Optional[str] = PrivateAttr(default=None)
    _token_expiry: Optional[datetime] = PrivateAttr(default=None)

    async def _call_api(self, **params) -> Dict[str, Any]:
        api_params = {
            "originLocationCode": params.get("origin").upper(),
            "destinationLocationCode": params.get("destination").upper(),
            "departureDate": params.get("departure_date"),
            "adults": params.get("adults", 1),
            "travelClass": params.get("travel_class", "ECONOMY"),
            "max": min(params.get("max_results", 5), 250),
            "currencyCode": "USD",
        }

        if params.get("return_date"):
            api_params["returnDate"] = params["return_date"]

        response = await self._make_amadeus_request(
            "GET",
            "/v2/shopping/flight-offers",
            params=api_params,
        )

        return response.json()

    def _normalize_response(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        offers = raw_data.get("data", [])
        dictionaries = raw_data.get("dictionaries", {})

        flights = []
        for offer in offers:
            price = offer.get("price", {})
            total_price = float(price.get("total", 0))
            currency = price.get("currency", "USD")

            itineraries = []
            for itinerary in offer.get("itineraries", []):
                segments = []
                total_duration = itinerary.get("duration", "")

                for segment in itinerary.get("segments", []):
                    departure = segment.get("departure", {})
                    arrival = segment.get("arrival", {})

                    segments.append({
                        "departure_airport": departure.get("iataCode"),
                        "departure_time": departure.get("at"),
                        "arrival_airport": arrival.get("iataCode"),
                        "arrival_time": arrival.get("at"),
                        "airline": segment.get("carrierCode"),
                        "flight_number": segment.get("number"),
                        "duration": segment.get("duration"),
                        "aircraft": segment.get("aircraft", {}).get("code"),
                    })

                itineraries.append({
                    "segments": segments,
                    "duration": total_duration,
                })

            flights.append({
                "id": offer.get("id"),
                "price": total_price,
                "currency": currency,
                "itineraries": itineraries,
                "number_of_bookable_seats": offer.get("numberOfBookableSeats", 0),
                "one_way": len(itineraries) == 1,
            })

        return {
            "flights": flights,
            "count": len(flights),
            "dictionaries": dictionaries,
        }


class HotelSearchInput(BaseModel):
    """Input schema for hotel search tool."""
    city_code: str = Field(description="City IATA code (e.g., NYC, PAR, LON)")
    check_in: str = Field(description="Check-in date (YYYY-MM-DD)")
    check_out: str = Field(description="Check-out date (YYYY-MM-DD)")
    adults: int = Field(default=1, description="Number of adults (1-9)")
    radius: int = Field(default=5, description="Search radius in km (0-300)")
    max_results: int = Field(default=10, description="Maximum number of results")


class HotelSearchTool(AmadeusAuthMixin, BaseTravelAPITool):
    """Search for hotel offers using Amadeus API."""

    name: str = "hotel_search"
    description: str = """Search for hotel offers in a city.
    Input should include city code (e.g., 'NYC'), check-in date (YYYY-MM-DD),
    check-out date, and number of adults.
    Returns hotel options with prices, ratings, and amenities."""

    args_schema: type[BaseModel] = HotelSearchInput

    api_name: str = "amadeus"
    cache_prefix: str = "hotel"

    _access_token: Optional[str] = PrivateAttr(default=None)
    _token_expiry: Optional[datetime] = PrivateAttr(default=None)

    async def _call_api(self, **params) -> Dict[str, Any]:
        city_code = params.get("city_code", "").upper()
        check_in = params.get("check_in")
        check_out = params.get("check_out")
        adults = params.get("adults", 1)
        radius = params.get("radius", 5)
        max_results = params.get("max_results", 10)

        list_response = await self._make_amadeus_request(
            "GET",
            "/v1/reference-data/locations/hotels/by-city",
            params={
                "cityCode": city_code,
                "radius": radius,
                "radiusUnit": "KM",
                "hotelSource": "ALL",
            },
        )

        list_data = list_response.json()
        hotel_list = list_data.get("data", [])

        if not hotel_list:
            return {"data": []}

        hotel_ids = [h.get("hotelId") for h in hotel_list[:max_results] if h.get("hotelId")]

        if not hotel_ids:
            return {"data": []}

        offers_response = await self._make_amadeus_request(
            "GET",
            "/v3/shopping/hotel-offers",
            params={
                "hotelIds": ",".join(hotel_ids[:10]),
                "checkInDate": check_in,
                "checkOutDate": check_out,
                "adults": adults,
                "bestRateOnly": "true",
                "currency": "USD",
            },
        )

        return offers_response.json()

    def _normalize_response(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        hotels_data = raw_data.get("data", [])

        hotels = []
        for hotel_data in hotels_data:
            hotel_info = hotel_data.get("hotel", {})
            offers = hotel_data.get("offers", [])

            best_offer = offers[0] if offers else {}
            price = best_offer.get("price", {})

            hotels.append({
                "hotel_id": hotel_info.get("hotelId"),
                "name": hotel_info.get("name"),
                "rating": hotel_info.get("rating"),
                "latitude": hotel_info.get("latitude"),
                "longitude": hotel_info.get("longitude"),
                "address": hotel_info.get("address", {}),
                "price": {
                    "total": price.get("total"),
                    "currency": price.get("currency", "USD"),
                    "per_night": price.get("base"),
                },
                "check_in": best_offer.get("checkInDate"),
                "check_out": best_offer.get("checkOutDate"),
                "room_type": best_offer.get("room", {}).get("typeEstimated", {}).get("category"),
                "beds": best_offer.get("room", {}).get("typeEstimated", {}).get("beds"),
                "guests": best_offer.get("guests", {}).get("adults", 1),
            })

        return {
            "hotels": hotels,
            "count": len(hotels),
        }