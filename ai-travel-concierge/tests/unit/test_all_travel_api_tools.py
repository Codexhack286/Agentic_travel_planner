"""
Unit tests for all 6 Travel API tools:
  1. WeatherForecastTool     (Open-Meteo       — no API key)
  2. CurrencyConversionTool  (Frankfurter      — no API key)
  3. CurrencyListTool        (Frankfurter      — no API key)
  4. CountryInfoTool         (REST Countries   — no API key)
  5. FlightSearchTool        (Amadeus          — AMADEUS_API_KEY + AMADEUS_API_SECRET)
  6. HotelSearchTool         (Amadeus          — same keys)
  7. UnsplashImageTool       (Unsplash         — UNSPLASH_ACCESS_KEY)
  8. VisaRequirementTool     (TravelBuddyAI    — PASSPORT_API_KEY)

Run:
    pytest tests/unit/test_all_travel_api_tools.py -v

No real API keys needed — all HTTP calls are mocked.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from src.tools.external_apis.weather_tools import WeatherForecastTool
from src.tools.external_apis.currency_tools import CurrencyConversionTool, CurrencyListTool
from src.tools.external_apis.country_tools import CountryInfoTool
from src.tools.external_apis.amadeus_tools import FlightSearchTool, HotelSearchTool
from src.tools.external_apis.image_tools import UnsplashImageTool, format_unsplash_attribution
from src.tools.external_apis.visa_tools import VisaRequirementTool, get_country_code, COUNTRY_CODES


# ===========================================================================
# Shared fixtures
# ===========================================================================

@pytest.fixture
def mock_cache_manager():
    """Cache manager that always returns a miss (None)."""
    m = MagicMock()
    m.get = AsyncMock(return_value=None)
    m.set = AsyncMock(return_value=True)
    return m


@pytest.fixture
def mock_rate_limiter():
    """Rate limiter that always grants permission immediately."""
    m = MagicMock()
    m.acquire_with_retry = AsyncMock(return_value=True)
    return m


def _mock_http(json_data: dict) -> MagicMock:
    """Helper: build a fake httpx response returning json_data."""
    resp = MagicMock()
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    return resp


def _http_error(status_code: int) -> httpx.HTTPStatusError:
    return httpx.HTTPStatusError(
        str(status_code),
        request=MagicMock(),
        response=MagicMock(status_code=status_code, text="error"),
    )


# ===========================================================================
# 1. WeatherForecastTool
# ===========================================================================

GEOCODE_RESPONSE = {
    "results": [{"latitude": 48.8566, "longitude": 2.3522, "name": "Paris", "country": "France"}]
}

WEATHER_RESPONSE = {
    "_formatted_location": "Paris, France",
    "latitude": 48.8566,
    "longitude": 2.3522,
    "timezone": "Europe/Paris",
    "current_weather": {
        "temperature": 18.5,
        "windspeed": 12.0,
        "winddirection": 270,
        "weathercode": 1,
        "time": "2026-03-01T12:00",
    },
    "daily": {
        "time": ["2026-03-01", "2026-03-02"],
        "temperature_2m_max": [20.0, 22.0],
        "temperature_2m_min": [12.0, 14.0],
        "precipitation_sum": [0.0, 2.5],
        "weathercode": [1, 61],
        "windspeed_10m_max": [15.0, 20.0],
    },
    "daily_units": {"temperature_2m_max": "°C"},
}


@pytest.fixture
def weather_tool(mock_cache_manager, mock_rate_limiter):
    tool = WeatherForecastTool(cache_manager=mock_cache_manager)
    tool.__class__._rate_limiter = mock_rate_limiter
    return tool


class TestWeatherForecastTool:

    def test_tool_metadata(self, weather_tool):
        assert weather_tool.name == "weather_forecast"
        assert weather_tool.api_name == "open_meteo"
        assert weather_tool.cache_prefix == "weather"
        assert "weather" in weather_tool.description.lower()

    def test_no_api_key_required(self):
        """Weather tool needs no env var — must not raise."""
        with patch.dict("os.environ", {}, clear=True):
            tool = WeatherForecastTool()
            assert tool is not None

    def test_normalize_response_structure(self, weather_tool):
        result = weather_tool._normalize_response(WEATHER_RESPONSE)
        assert result["location"] == "Paris, France"
        assert result["current"]["temperature"] == 18.5
        assert result["current"]["condition"] == "Mainly clear"
        assert len(result["forecast"]) == 2

    def test_forecast_fields(self, weather_tool):
        result = weather_tool._normalize_response(WEATHER_RESPONSE)
        day = result["forecast"][0]
        assert day["date"] == "2026-03-01"
        assert day["high"] == 20.0
        assert day["low"] == 12.0
        assert day["condition"] == "Mainly clear"
        assert day["precipitation_mm"] == 0.0

    def test_weather_code_mapping(self, weather_tool):
        assert weather_tool.WEATHER_CODES[0] == "Clear sky"
        assert weather_tool.WEATHER_CODES[61] == "Slight rain"
        assert weather_tool.WEATHER_CODES[95] == "Thunderstorm"

    @pytest.mark.asyncio
    async def test_successful_execute(self, weather_tool):
        with patch.object(weather_tool, "_make_request", new=AsyncMock(
            side_effect=[_mock_http(GEOCODE_RESPONSE), _mock_http(WEATHER_RESPONSE)]
        )):
            result = await weather_tool.execute(location="Paris, France", days=2)

        assert result.success is True
        assert result.source == "open_meteo"
        assert result.data["location"] == "Paris, France"

    @pytest.mark.asyncio
    async def test_location_not_found(self, weather_tool):
        with patch.object(weather_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http({"results": []})
        )):
            result = await weather_tool.execute(location="Neverland")

        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_days_capped_at_16(self, weather_tool):
        calls = []
        async def fake_request(method, url, **kwargs):
            calls.append((url, kwargs))
            if "geocoding" in url:
                return _mock_http(GEOCODE_RESPONSE)
            return _mock_http(WEATHER_RESPONSE)

        with patch.object(weather_tool, "_make_request", new=fake_request):
            await weather_tool.execute(location="Paris", days=99)

        forecast_call = next(c for c in calls if "forecast" in c[0])
        assert forecast_call[1]["params"]["forecast_days"] == 16

    @pytest.mark.asyncio
    async def test_cache_hit_skips_api(self, weather_tool, mock_cache_manager):
        mock_cache_manager.get = AsyncMock(return_value={"location": "Cached"})
        with patch.object(weather_tool, "_make_request", new=AsyncMock()) as m:
            result = await weather_tool.execute(location="Paris")
            m.assert_not_called()
        assert result.cached is True

    @pytest.mark.asyncio
    async def test_http_error_returns_failure(self, weather_tool):
        with patch.object(weather_tool, "_make_request", new=AsyncMock(
            side_effect=[_mock_http(GEOCODE_RESPONSE), _http_error(500)]
        )):
            result = await weather_tool.execute(location="Paris")
        assert result.success is False


# ===========================================================================
# 2. CurrencyConversionTool
# ===========================================================================

CURRENCY_RESPONSE = {
    "amount": 100.0,
    "base": "USD",
    "date": "2026-03-01",
    "rates": {"EUR": 91.5},
}


@pytest.fixture
def currency_tool(mock_cache_manager, mock_rate_limiter):
    tool = CurrencyConversionTool(cache_manager=mock_cache_manager)
    tool.__class__._rate_limiter = mock_rate_limiter
    return tool


class TestCurrencyConversionTool:

    def test_tool_metadata(self, currency_tool):
        assert currency_tool.name == "currency_conversion"
        assert currency_tool.api_name == "frankfurter"
        assert "currency" in currency_tool.description.lower()

    def test_no_api_key_required(self):
        with patch.dict("os.environ", {}, clear=True):
            tool = CurrencyConversionTool()
            assert tool is not None

    def test_normalize_response(self, currency_tool):
        result = currency_tool._normalize_response(CURRENCY_RESPONSE)
        assert result["original_amount"] == 100.0
        assert result["original_currency"] == "USD"
        assert result["converted_amount"] == 91.5
        assert result["converted_currency"] == "EUR"
        assert abs(result["exchange_rate"] - 0.915) < 0.001
        assert "USD" in result["formula"]
        assert "EUR" in result["formula"]

    def test_unsupported_currency_raises(self, currency_tool):
        with pytest.raises(ValueError, match="Unsupported currency"):
            import asyncio
            asyncio.run(
                currency_tool._call_api(amount=100, from_currency="XYZ", to_currency="USD")
            )

    @pytest.mark.asyncio
    async def test_successful_conversion(self, currency_tool):
        with patch.object(currency_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http(CURRENCY_RESPONSE)
        )):
            result = await currency_tool.execute(amount=100, from_currency="USD", to_currency="EUR")

        assert result.success is True
        assert result.data["converted_currency"] == "EUR"

    @pytest.mark.asyncio
    async def test_historical_date_uses_correct_url(self, currency_tool):
        with patch.object(currency_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http(CURRENCY_RESPONSE)
        )) as m:
            await currency_tool.execute(
                amount=100, from_currency="USD", to_currency="EUR", date="2025-01-01"
            )
            url = m.call_args[0][1]
            assert "2025-01-01" in url

    @pytest.mark.asyncio
    async def test_latest_rate_url(self, currency_tool):
        with patch.object(currency_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http(CURRENCY_RESPONSE)
        )) as m:
            await currency_tool.execute(amount=50, from_currency="USD", to_currency="EUR")
            url = m.call_args[0][1]
            assert "latest" in url

    @pytest.mark.asyncio
    async def test_http_error_returns_failure(self, currency_tool):
        with patch.object(currency_tool, "_make_request", new=AsyncMock(
            side_effect=_http_error(429)
        )):
            result = await currency_tool.execute(amount=100, from_currency="USD", to_currency="EUR")
        assert result.success is False
        assert "Rate limit" in result.error


# ===========================================================================
# 3. CurrencyListTool
# ===========================================================================

CURRENCY_LIST_RESPONSE = {
    "USD": "United States Dollar",
    "EUR": "Euro",
    "JPY": "Japanese Yen",
    "GBP": "British Pound Sterling",
}


@pytest.fixture
def currency_list_tool(mock_cache_manager, mock_rate_limiter):
    tool = CurrencyListTool(cache_manager=mock_cache_manager)
    tool.__class__._rate_limiter = mock_rate_limiter
    return tool


class TestCurrencyListTool:

    def test_tool_metadata(self, currency_list_tool):
        assert currency_list_tool.name == "list_currencies"
        assert currency_list_tool.api_name == "frankfurter"

    def test_normalize_response(self, currency_list_tool):
        result = currency_list_tool._normalize_response(CURRENCY_LIST_RESPONSE)
        assert result["count"] == 4
        codes = [c["code"] for c in result["currencies"]]
        assert "USD" in codes
        assert "EUR" in codes

    @pytest.mark.asyncio
    async def test_successful_list(self, currency_list_tool):
        with patch.object(currency_list_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http(CURRENCY_LIST_RESPONSE)
        )):
            result = await currency_list_tool.execute()
        assert result.success is True
        assert result.data["count"] == 4


# ===========================================================================
# 4. CountryInfoTool
# ===========================================================================

COUNTRY_RESPONSE = {
    "name": {"common": "Japan", "official": "Japan"},
    "cca2": "JP",
    "cca3": "JPN",
    "capital": ["Tokyo"],
    "region": "Asia",
    "subregion": "Eastern Asia",
    "currencies": {"JPY": {"name": "Japanese yen", "symbol": "¥"}},
    "languages": {"jpn": "Japanese"},
    "population": 125700000,
    "area": 377930.0,
    "timezones": ["UTC+09:00"],
    "borders": ["KOR", "PRK", "RUS"],
    "car": {"side": "left"},
    "flags": {"png": "https://flagcdn.com/jp.png"},
    "coatOfArms": {},
    "maps": {"googleMaps": "https://goo.gl/maps/Japan"},
    "demonyms": {"eng": {"m": "Japanese", "f": "Japanese"}},
}


@pytest.fixture
def country_tool(mock_cache_manager, mock_rate_limiter):
    tool = CountryInfoTool(cache_manager=mock_cache_manager)
    tool.__class__._rate_limiter = mock_rate_limiter
    return tool


class TestCountryInfoTool:

    def test_tool_metadata(self, country_tool):
        assert country_tool.name == "country_info"
        assert country_tool.api_name == "rest_countries"
        assert "country" in country_tool.description.lower()

    def test_no_api_key_required(self):
        with patch.dict("os.environ", {}, clear=True):
            tool = CountryInfoTool()
            assert tool is not None

    def test_normalize_response(self, country_tool):
        result = country_tool._normalize_response(COUNTRY_RESPONSE)
        assert result["name"]["common"] == "Japan"
        assert result["codes"]["iso_alpha_2"] == "JP"
        assert result["capital"] == "Tokyo"
        assert result["region"] == "Asia"
        assert result["primary_currency"]["code"] == "JPY"
        assert result["primary_currency"]["symbol"] == "¥"
        assert "Japanese" in result["languages"]
        assert result["population"] == 125700000
        assert result["timezone"] == "UTC+09:00"
        assert result["driving_side"] == "left"
        assert result["flag_url"] == "https://flagcdn.com/jp.png"

    def test_empty_query_raises(self, country_tool):
        import asyncio
        with pytest.raises(ValueError):
            asyncio.run(
                country_tool._call_api(query="")
            )

    @pytest.mark.asyncio
    async def test_search_by_name(self, country_tool):
        with patch.object(country_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http([COUNTRY_RESPONSE])
        )) as m:
            await country_tool.execute(query="Japan", search_by="name")
            assert "/name/Japan" in m.call_args[0][1]

    @pytest.mark.asyncio
    async def test_search_by_code(self, country_tool):
        with patch.object(country_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http([COUNTRY_RESPONSE])
        )) as m:
            await country_tool.execute(query="JP", search_by="code")
            assert "/alpha/JP" in m.call_args[0][1]

    @pytest.mark.asyncio
    async def test_search_by_capital(self, country_tool):
        with patch.object(country_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http([COUNTRY_RESPONSE])
        )) as m:
            await country_tool.execute(query="Tokyo", search_by="capital")
            assert "/capital/Tokyo" in m.call_args[0][1]

    @pytest.mark.asyncio
    async def test_not_found_returns_failure(self, country_tool):
        with patch.object(country_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http([])
        )):
            result = await country_tool.execute(query="Neverland")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_http_404_returns_failure(self, country_tool):
        with patch.object(country_tool, "_make_request", new=AsyncMock(
            side_effect=_http_error(404)
        )):
            result = await country_tool.execute(query="Unknownland")
        assert result.success is False


# ===========================================================================
# 5. FlightSearchTool
# ===========================================================================

AMADEUS_TOKEN_RESPONSE = {
    "access_token": "test-amadeus-token",
    "expires_in": 1799,
}

FLIGHT_SEARCH_RESPONSE = {
    "data": [
        {
            "id": "1",
            "price": {"total": "450.00", "currency": "USD"},
            "numberOfBookableSeats": 9,
            "itineraries": [
                {
                    "duration": "PT7H30M",
                    "segments": [
                        {
                            "departure": {"iataCode": "JFK", "at": "2026-06-01T08:00"},
                            "arrival": {"iataCode": "LHR", "at": "2026-06-01T20:00"},
                            "carrierCode": "BA",
                            "number": "178",
                            "duration": "PT7H30M",
                            "aircraft": {"code": "777"},
                        }
                    ],
                }
            ],
        }
    ],
    "dictionaries": {"carriers": {"BA": "British Airways"}},
}


@pytest.fixture
def flight_tool(mock_cache_manager, mock_rate_limiter):
    with patch.dict("os.environ", {
        "AMADEUS_API_KEY": "test-amadeus-key",
        "AMADEUS_API_SECRET": "test-amadeus-secret",
    }):
        tool = FlightSearchTool(cache_manager=mock_cache_manager)
        tool.__class__._rate_limiter = mock_rate_limiter
        # Pre-load token so _get_access_token is never called during tests
        tool._access_token = "test-amadeus-token"
        from datetime import datetime, timedelta
        tool._token_expiry = datetime.now() + timedelta(hours=1)
        return tool


class TestFlightSearchTool:

    def test_tool_metadata(self, flight_tool):
        assert flight_tool.name == "flight_search"
        assert flight_tool.api_name == "amadeus"
        assert flight_tool.cache_prefix == "flight"

    def test_normalize_response(self, flight_tool):
        result = flight_tool._normalize_response(FLIGHT_SEARCH_RESPONSE)
        assert result["count"] == 1
        flight = result["flights"][0]
        assert flight["price"] == 450.0
        assert flight["currency"] == "USD"
        seg = flight["itineraries"][0]["segments"][0]
        assert seg["departure_airport"] == "JFK"
        assert seg["arrival_airport"] == "LHR"
        assert seg["airline"] == "BA"

    @pytest.mark.asyncio
    async def test_successful_search(self, flight_tool):
        # FIX: The token is pre-loaded by the fixture, so we only expect 1 HTTP request for the flight data
        with patch.object(flight_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http(FLIGHT_SEARCH_RESPONSE)
        )):
            result = await flight_tool.execute(
                origin="JFK", destination="LHR",
                departure_date="2026-06-01", adults=1
            )
        assert result.success is True
        assert result.data["count"] == 1

    @pytest.mark.asyncio
    async def test_origin_destination_uppercased(self, flight_tool):
        calls = []
        async def fake_req(method, url, **kwargs):
            calls.append((method, url, kwargs))
            if "oauth2" in url:
                return _mock_http(AMADEUS_TOKEN_RESPONSE)
            return _mock_http(FLIGHT_SEARCH_RESPONSE)

        with patch.object(flight_tool, "_make_request", new=fake_req):
            await flight_tool.execute(
                origin="jfk", destination="lhr", departure_date="2026-06-01"
            )
        flight_call = next(c for c in calls if "flight-offers" in c[1])
        assert flight_call[2]["params"]["originLocationCode"] == "JFK"
        assert flight_call[2]["params"]["destinationLocationCode"] == "LHR"

    @pytest.mark.asyncio
    async def test_round_trip_includes_return_date(self, flight_tool):
        calls = []
        async def fake_req(method, url, **kwargs):
            calls.append((method, url, kwargs))
            if "oauth2" in url:
                return _mock_http(AMADEUS_TOKEN_RESPONSE)
            return _mock_http(FLIGHT_SEARCH_RESPONSE)

        with patch.object(flight_tool, "_make_request", new=fake_req):
            await flight_tool.execute(
                origin="JFK", destination="LHR",
                departure_date="2026-06-01", return_date="2026-06-15"
            )
        flight_call = next(c for c in calls if "flight-offers" in c[1])
        assert "returnDate" in flight_call[2]["params"]

    @pytest.mark.asyncio
    async def test_max_results_capped_at_250(self, flight_tool):
        calls = []
        async def fake_req(method, url, **kwargs):
            calls.append((method, url, kwargs))
            if "oauth2" in url:
                return _mock_http(AMADEUS_TOKEN_RESPONSE)
            return _mock_http(FLIGHT_SEARCH_RESPONSE)

        with patch.object(flight_tool, "_make_request", new=fake_req):
            await flight_tool.execute(
                origin="JFK", destination="LHR",
                departure_date="2026-06-01", max_results=999
            )
        flight_call = next(c for c in calls if "flight-offers" in c[1])
        assert flight_call[2]["params"]["max"] == 250

    @pytest.mark.asyncio
    async def test_token_reused_if_valid(self, flight_tool):
        """When token is valid, only one HTTP call is made (no re-auth)."""
        with patch.object(flight_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http(FLIGHT_SEARCH_RESPONSE)
        )) as m:
            await flight_tool.execute(
                origin="JFK", destination="LHR", departure_date="2026-06-01"
            )
            # Only one HTTP call (flight search, no token fetch)
            assert m.call_count == 1

    @pytest.mark.asyncio
    async def test_missing_credentials_returns_failure(self, mock_cache_manager, mock_rate_limiter):
        with patch.dict("os.environ", {}, clear=True):
            tool = FlightSearchTool(cache_manager=mock_cache_manager)
            tool.__class__._rate_limiter = mock_rate_limiter
            # Token is None/expired, so _get_access_token will check env and fail
            result = await tool.execute(
                origin="JFK", destination="LHR", departure_date="2026-06-01"
            )
        assert result.success is False
        assert "credential" in result.error.lower()

    @pytest.mark.asyncio
    async def test_http_error_returns_failure(self, flight_tool):
        with patch.object(flight_tool, "_make_request", new=AsyncMock(
            side_effect=_http_error(401)
        )):
            result = await flight_tool.execute(
                origin="JFK", destination="LHR", departure_date="2026-06-01"
            )
        assert result.success is False


# ===========================================================================
# 6. HotelSearchTool
# ===========================================================================

HOTEL_LIST_RESPONSE = {
    "data": [
        {"hotelId": "ADPAR001"},
        {"hotelId": "ADPAR002"},
    ]
}

HOTEL_OFFERS_RESPONSE = {
    "data": [
        {
            "hotel": {
                "hotelId": "ADPAR001",
                "name": "Hotel Le Marais",
                "rating": "4",
                "latitude": 48.8566,
                "longitude": 2.3522,
                "address": {"cityName": "Paris"},
            },
            "offers": [
                {
                    "checkInDate": "2026-06-01",
                    "checkOutDate": "2026-06-05",
                    "price": {"total": "620.00", "base": "155.00", "currency": "USD"},
                    "room": {"typeEstimated": {"category": "STANDARD_ROOM", "beds": 1}},
                    "guests": {"adults": 2},
                }
            ],
        }
    ]
}


@pytest.fixture
def hotel_tool(mock_cache_manager, mock_rate_limiter):
    with patch.dict("os.environ", {
        "AMADEUS_API_KEY": "test-amadeus-key",
        "AMADEUS_API_SECRET": "test-amadeus-secret",
    }):
        tool = HotelSearchTool(cache_manager=mock_cache_manager)
        tool.__class__._rate_limiter = mock_rate_limiter
        tool._access_token = "pre-loaded-token"
        from datetime import datetime, timedelta
        tool._token_expiry = datetime.now() + timedelta(hours=1)
        return tool


class TestHotelSearchTool:

    def test_tool_metadata(self, hotel_tool):
        assert hotel_tool.name == "hotel_search"
        assert hotel_tool.api_name == "amadeus"
        assert hotel_tool.cache_prefix == "hotel"

    def test_normalize_response(self, hotel_tool):
        result = hotel_tool._normalize_response(HOTEL_OFFERS_RESPONSE)
        assert result["count"] == 1
        hotel = result["hotels"][0]
        assert hotel["name"] == "Hotel Le Marais"
        assert hotel["rating"] == "4"
        assert hotel["price"]["total"] == "620.00"
        assert hotel["room_type"] == "STANDARD_ROOM"

    def test_empty_response(self, hotel_tool):
        result = hotel_tool._normalize_response({"data": []})
        assert result["count"] == 0
        assert result["hotels"] == []

    @pytest.mark.asyncio
    async def test_successful_search(self, hotel_tool):
        with patch.object(hotel_tool, "_make_request", new=AsyncMock(side_effect=[
            _mock_http(HOTEL_LIST_RESPONSE),
            _mock_http(HOTEL_OFFERS_RESPONSE),
        ])):
            result = await hotel_tool.execute(
                city_code="PAR", check_in="2026-06-01",
                check_out="2026-06-05", adults=2
            )
        assert result.success is True
        assert result.data["count"] == 1

    @pytest.mark.asyncio
    async def test_city_code_uppercased(self, hotel_tool):
        calls = []
        async def fake_req(method, url, **kwargs):
            calls.append((method, url, kwargs))
            if "by-city" in url:
                return _mock_http(HOTEL_LIST_RESPONSE)
            return _mock_http(HOTEL_OFFERS_RESPONSE)

        with patch.object(hotel_tool, "_make_request", new=fake_req):
            await hotel_tool.execute(
                city_code="par", check_in="2026-06-01", check_out="2026-06-05"
            )
        city_call = next(c for c in calls if "by-city" in c[1])
        assert city_call[2]["params"]["cityCode"] == "PAR"

    @pytest.mark.asyncio
    async def test_empty_hotel_list_returns_empty(self, hotel_tool):
        with patch.object(hotel_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http({"data": []})
        )):
            result = await hotel_tool.execute(
                city_code="XYZ", check_in="2026-06-01", check_out="2026-06-05"
            )
        assert result.success is True
        assert result.data["count"] == 0

    @pytest.mark.asyncio
    async def test_hotel_ids_limited_to_10(self, hotel_tool):
        many_hotels = {"data": [{"hotelId": f"H{i:03d}"} for i in range(20)]}
        calls = []
        async def fake_req(method, url, **kwargs):
            calls.append((method, url, kwargs))
            if "by-city" in url:
                return _mock_http(many_hotels)
            return _mock_http(HOTEL_OFFERS_RESPONSE)

        with patch.object(hotel_tool, "_make_request", new=fake_req):
            await hotel_tool.execute(
                city_code="PAR", check_in="2026-06-01", check_out="2026-06-05"
            )
        offers_call = next(c for c in calls if "hotel-offers" in c[1])
        hotel_ids = offers_call[2]["params"]["hotelIds"].split(",")
        assert len(hotel_ids) <= 10


# ===========================================================================
# 7. UnsplashImageTool
# ===========================================================================

UNSPLASH_RESPONSE = {
    "total": 2,
    "results": [
        {
            "id": "abc123",
            "description": "Eiffel Tower at sunset",
            "alt_description": "eiffel tower paris",
            "urls": {
                "raw": "https://images.unsplash.com/photo?raw",
                "full": "https://images.unsplash.com/photo?full",
                "regular": "https://images.unsplash.com/photo?regular",
                "small": "https://images.unsplash.com/photo?small",
                "thumb": "https://images.unsplash.com/photo?thumb",
            },
            "width": 4000, "height": 3000, "color": "#c0a080",
            "user": {
                "name": "Jane Photographer",
                "username": "janephoto",
                "links": {"html": "https://unsplash.com/@janephoto"},
            },
            "links": {
                "html": "https://unsplash.com/photos/abc123",
                "download_location": "https://api.unsplash.com/photos/abc123/download",
            },
        },
        {
            "id": "def456",
            "description": None,
            "alt_description": "paris skyline night",
            "urls": {
                "raw": "https://images.unsplash.com/photo2?raw",
                "full": "https://images.unsplash.com/photo2?full",
                "regular": "https://images.unsplash.com/photo2?regular",
                "small": "https://images.unsplash.com/photo2?small",
                "thumb": "https://images.unsplash.com/photo2?thumb",
            },
            "width": 5000, "height": 3500, "color": "#000000",
            "user": {
                "name": "Bob Travels",
                "username": "bobtravels",
                "links": {"html": "https://unsplash.com/@bobtravels"},
            },
            "links": {
                "html": "https://unsplash.com/photos/def456",
                "download_location": "https://api.unsplash.com/photos/def456/download",
            },
        },
    ],
}


@pytest.fixture
def image_tool(mock_cache_manager, mock_rate_limiter):
    with patch.dict("os.environ", {"UNSPLASH_ACCESS_KEY": "test-unsplash-key"}):
        tool = UnsplashImageTool(cache_manager=mock_cache_manager)
        tool.__class__._rate_limiter = mock_rate_limiter
        return tool


class TestUnsplashImageTool:

    def test_init_with_key(self):
        with patch.dict("os.environ", {"UNSPLASH_ACCESS_KEY": "mykey"}):
            tool = UnsplashImageTool()
            assert tool.access_key == "mykey"

    def test_init_without_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="UNSPLASH_ACCESS_KEY"):
                UnsplashImageTool()

    def test_tool_metadata(self, image_tool):
        assert image_tool.name == "search_destination_images"
        assert image_tool.api_name == "unsplash"
        assert image_tool.cache_prefix == "images"

    def test_normalize_response(self, image_tool):
        result = image_tool._normalize_response(UNSPLASH_RESPONSE)
        assert result["total_results"] == 2
        assert result["returned_count"] == 2
        assert result["attribution_required"] is True

    def test_image_fields_complete(self, image_tool):
        result = image_tool._normalize_response(UNSPLASH_RESPONSE)
        img = result["images"][0]
        assert img["id"] == "abc123"
        assert img["description"] == "Eiffel Tower at sunset"
        assert img["urls"]["regular"].endswith("?regular")
        assert img["photographer"]["name"] == "Jane Photographer"
        assert img["download_location"] is not None

    def test_alt_description_fallback(self, image_tool):
        result = image_tool._normalize_response(UNSPLASH_RESPONSE)
        # Second image has description=None, should use alt_description
        assert result["images"][1]["description"] == "paris skyline night"

    def test_per_page_capped_at_30(self, image_tool):
        import asyncio
        with patch.object(image_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http({"total": 0, "results": []})
        )) as m:
            asyncio.run(
                image_tool._call_api(query="Tokyo", per_page=999)
            )
            assert m.call_args[1]["params"]["per_page"] == 30

    def test_invalid_orientation_ignored(self, image_tool):
        import asyncio
        with patch.object(image_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http({"total": 0, "results": []})
        )) as m:
            asyncio.run(
                image_tool._call_api(query="Tokyo", orientation="diagonal")
            )
            assert "orientation" not in m.call_args[1]["params"]

    def test_valid_orientation_passed(self, image_tool):
        import asyncio
        with patch.object(image_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http({"total": 0, "results": []})
        )) as m:
            asyncio.run(
                image_tool._call_api(query="Paris", orientation="landscape")
            )
            assert m.call_args[1]["params"]["orientation"] == "landscape"

    def test_auth_header_format(self, image_tool):
        import asyncio
        with patch.object(image_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http({"total": 0, "results": []})
        )) as m:
            asyncio.run(
                image_tool._call_api(query="Rome")
            )
            assert m.call_args[1]["headers"]["Authorization"] == "Client-ID test-unsplash-key"
            assert m.call_args[1]["headers"]["Accept-Version"] == "v1"

    @pytest.mark.asyncio
    async def test_successful_execute(self, image_tool):
        with patch.object(image_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http(UNSPLASH_RESPONSE)
        )):
            result = await image_tool.execute(query="Paris Eiffel Tower", per_page=2)
        assert result.success is True
        assert result.data["returned_count"] == 2

    @pytest.mark.asyncio
    async def test_empty_query_raises(self, image_tool):
        result = await image_tool.execute(query="")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_http_401_returns_failure(self, image_tool):
        with patch.object(image_tool, "_make_request", new=AsyncMock(
            side_effect=_http_error(401)
        )):
            result = await image_tool.execute(query="Paris")
        assert result.success is False
        assert "Authentication failed" in result.error

    @pytest.mark.asyncio
    async def test_http_429_returns_failure(self, image_tool):
        with patch.object(image_tool, "_make_request", new=AsyncMock(
            side_effect=_http_error(429)
        )):
            result = await image_tool.execute(query="Paris")
        assert result.success is False
        assert "Rate limit" in result.error

    @pytest.mark.asyncio
    async def test_cache_hit(self, image_tool, mock_cache_manager):
        mock_cache_manager.get = AsyncMock(return_value={"total_results": 5, "images": []})
        with patch.object(image_tool, "_make_request", new=AsyncMock()) as m:
            result = await image_tool.execute(query="Cached")
            m.assert_not_called()
        assert result.cached is True


class TestFormatUnsplashAttribution:

    def test_formats_correctly(self):
        img = {"photographer": {"name": "Jane Doe"}}
        assert format_unsplash_attribution(img) == "Photo by Jane Doe on Unsplash"

    def test_missing_photographer_name(self):
        assert format_unsplash_attribution({}) == "Photo by Unknown on Unsplash"
        assert format_unsplash_attribution({"photographer": {}}) == "Photo by Unknown on Unsplash"


# ===========================================================================
# 8. VisaRequirementTool
# ===========================================================================

VISA_FREE_RESPONSE = {
    "data": {
        "passport": {"code": "US"},
        "destination": {"code": "JP"},
        "visaRules": {
            "primary": {
                "label": "Visa Free",
                "color": "green",
                "duration": "90 days",
                "exception": "Valid passport required",
                "link": None,
            }
        },
        "mandatoryRegistrations": [],
    }
}

VISA_REQUIRED_RESPONSE = {
    "data": {
        "passport": {"code": "IN"},
        "destination": {"code": "US"},
        "visaRules": {
            "primary": {
                "label": "Visa Required",
                "color": "red",
                "duration": "",
                "exception": "Apply at US Embassy",
                "link": None,
            }
        },
        "mandatoryRegistrations": [],
    }
}

VISA_ON_ARRIVAL_RESPONSE = {
    "data": {
        "passport": {"code": "GB"},
        "destination": {"code": "TH"},
        "visaRules": {
            "primary": {
                "label": "Visa on Arrival",
                "color": "blue",
                "duration": "30 days",
                "exception": "",
                "link": None,
            }
        },
        "mandatoryRegistrations": [
            {"name": "TM6 Arrival Card", "required": True, "link": "https://example.com/tm6"}
        ],
    }
}

EVISA_RESPONSE = {
    "data": {
        "passport": {"code": "AU"},
        "destination": {"code": "IN"},
        "visaRules": {
            "primary": {
                "label": "e-Visa",
                "color": "light_blue",
                "duration": "60 days",
                "exception": "",
                "link": "https://indianvisaonline.gov.in",
            }
        },
        "mandatoryRegistrations": [],
    }
}


@pytest.fixture
def visa_tool(mock_cache_manager, mock_rate_limiter):
    with patch.dict("os.environ", {"PASSPORT_API_KEY": "test-passport-key"}):
        tool = VisaRequirementTool(cache_manager=mock_cache_manager)
        tool.__class__._rate_limiter = mock_rate_limiter
        return tool


class TestVisaRequirementToolInit:

    def test_init_with_key(self):
        with patch.dict("os.environ", {"PASSPORT_API_KEY": "mykey"}):
            tool = VisaRequirementTool()
            assert tool.rapidapi_key == "mykey"

    def test_init_without_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="PASSPORT_API_KEY"):
                VisaRequirementTool()

    def test_tool_metadata(self, visa_tool):
        assert visa_tool.name == "check_visa_requirements"
        assert visa_tool.api_name == "travelbuddy_visa"
        assert visa_tool.cache_prefix == "visa"


class TestVisaCallApi:

    @pytest.mark.asyncio
    async def test_missing_country_raises(self, visa_tool):
        with pytest.raises(ValueError, match="required"):
            await visa_tool._call_api(from_country="", to_country="JP")

    @pytest.mark.asyncio
    async def test_invalid_code_length_raises(self, visa_tool):
        with pytest.raises(ValueError, match="2-letter"):
            await visa_tool._call_api(from_country="USA", to_country="JP")

    @pytest.mark.asyncio
    async def test_codes_uppercased(self, visa_tool):
        with patch.object(visa_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http(VISA_FREE_RESPONSE)
        )) as m:
            await visa_tool._call_api(from_country="us", to_country="jp")
            body = m.call_args[1]["json"]
            assert body["passport"] == "US"
            assert body["destination"] == "JP"

    @pytest.mark.asyncio
    async def test_correct_headers(self, visa_tool):
        with patch.object(visa_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http(VISA_FREE_RESPONSE)
        )) as m:
            await visa_tool._call_api(from_country="US", to_country="JP")
            headers = m.call_args[1]["headers"]
            assert headers["X-RapidAPI-Key"] == "test-passport-key"
            assert headers["X-RapidAPI-Host"] == "visa-requirement.p.rapidapi.com"

    @pytest.mark.asyncio
    async def test_uses_post_method(self, visa_tool):
        with patch.object(visa_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http(VISA_FREE_RESPONSE)
        )) as m:
            await visa_tool._call_api(from_country="US", to_country="JP")
            assert m.call_args[0][0] == "POST"


class TestVisaNormalization:

    def test_visa_free(self, visa_tool):
        result = visa_tool._normalize_response(VISA_FREE_RESPONSE)
        assert result["from_country"] == "US"
        assert result["to_country"] == "JP"
        assert result["category"] == "visa_free"
        assert result["duration"] == 90
        assert "No visa required" in result["summary"]
        assert "90 days" in result["summary"]

    def test_visa_required(self, visa_tool):
        result = visa_tool._normalize_response(VISA_REQUIRED_RESPONSE)
        assert result["category"] == "visa_required"
        assert result["duration"] is None
        assert "embassy" in result["summary"].lower()

    def test_visa_on_arrival(self, visa_tool):
        result = visa_tool._normalize_response(VISA_ON_ARRIVAL_RESPONSE)
        assert result["category"] == "visa_on_arrival"
        assert result["duration"] == 30
        assert len(result["registrations"]) == 1
        assert result["registrations"][0]["name"] == "TM6 Arrival Card"
        assert "registration" in result["summary"].lower()

    def test_evisa(self, visa_tool):
        result = visa_tool._normalize_response(EVISA_RESPONSE)
        assert result["category"] == "evisa"
        assert result["evisa_link"] == "https://indianvisaonline.gov.in"
        assert "online" in result["summary"].lower()


class TestVisaCategoryFallback:
    """Verify label-based category fallback when color is missing."""

    def test_visa_free_from_label(self, visa_tool):
        assert visa_tool._normalize_response({
            "data": {
                "passport": {"code": "US"}, "destination": {"code": "JP"},
                "visaRules": {"primary": {"label": "Visa Free", "color": ""}},
                "mandatoryRegistrations": [],
            }
        })["category"] == "visa_free"

    def test_visa_on_arrival_from_label(self, visa_tool):
        assert visa_tool._normalize_response({
            "data": {
                "passport": {"code": "GB"}, "destination": {"code": "TH"},
                "visaRules": {"primary": {"label": "Visa on Arrival", "color": ""}},
                "mandatoryRegistrations": [],
            }
        })["category"] == "visa_on_arrival"


class TestVisaParseDuration:

    def test_days(self, visa_tool):
        assert visa_tool._parse_duration("90 days") == 90

    def test_months(self, visa_tool):
        assert visa_tool._parse_duration("3 months") == 90

    def test_years(self, visa_tool):
        assert visa_tool._parse_duration("1 year") == 365

    def test_empty(self, visa_tool):
        assert visa_tool._parse_duration("") is None

    def test_no_number(self, visa_tool):
        assert visa_tool._parse_duration("varies") is None


class TestVisaExecute:

    @pytest.mark.asyncio
    async def test_successful_execute(self, visa_tool):
        with patch.object(visa_tool, "_make_request", new=AsyncMock(
            return_value=_mock_http(VISA_FREE_RESPONSE)
        )):
            result = await visa_tool.execute(from_country="US", to_country="JP")
        assert result.success is True
        assert result.data["category"] == "visa_free"
        assert result.source == "travelbuddy_visa"

    @pytest.mark.asyncio
    async def test_cache_hit(self, visa_tool, mock_cache_manager):
        mock_cache_manager.get = AsyncMock(return_value={"category": "visa_free"})
        with patch.object(visa_tool, "_make_request", new=AsyncMock()) as m:
            result = await visa_tool.execute(from_country="US", to_country="JP")
            m.assert_not_called()
        assert result.cached is True

    @pytest.mark.asyncio
    async def test_http_401_failure(self, visa_tool):
        with patch.object(visa_tool, "_make_request", new=AsyncMock(
            side_effect=_http_error(401)
        )):
            result = await visa_tool.execute(from_country="US", to_country="JP")
        assert result.success is False
        assert "Authentication failed" in result.error

    @pytest.mark.asyncio
    async def test_http_429_failure(self, visa_tool):
        with patch.object(visa_tool, "_make_request", new=AsyncMock(
            side_effect=_http_error(429)
        )):
            result = await visa_tool.execute(from_country="US", to_country="JP")
        assert result.success is False
        assert "Rate limit" in result.error

    @pytest.mark.asyncio
    async def test_validation_error_returned_as_failure(self, visa_tool):
        result = await visa_tool.execute(from_country="USA", to_country="JP")
        assert result.success is False
        assert "2-letter" in result.error


# ===========================================================================
# 9. get_country_code helper + COUNTRY_CODES integrity
# ===========================================================================

class TestGetCountryCode:

    def test_known_countries(self):
        assert get_country_code("Japan") == "JP"
        assert get_country_code("United States") == "US"
        assert get_country_code("United Kingdom") == "GB"
        assert get_country_code("India") == "IN"
        assert get_country_code("Australia") == "AU"
        assert get_country_code("United Arab Emirates") == "AE"

    def test_unknown_returns_none(self):
        assert get_country_code("Neverland") is None
        assert get_country_code("") is None

    def test_case_sensitive(self):
        assert get_country_code("japan") is None

    def test_all_codes_two_uppercase_letters(self):
        for name, code in COUNTRY_CODES.items():
            assert len(code) == 2, f"{name}: code '{code}' is not 2 chars"
            assert code.isupper(), f"{name}: code '{code}' is not uppercase"