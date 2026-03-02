"""
Visa Requirements API tool using RapidAPI Visa Requirement API.

Checks visa requirements between countries.
Free tier: 100 requests/month
"""
import os
import re
from typing import Dict, Any, Optional, ClassVar
from pydantic import BaseModel, Field, PrivateAttr

from .base import BaseTravelAPITool


class VisaRequirementInput(BaseModel):
    """Input schema for visa requirement check tool."""
    from_country: str = Field(
        description="Origin country code (ISO 3166-1 alpha-2, e.g., 'US', 'GB', 'IN')"
    )
    to_country: str = Field(
        description="Destination country code (ISO 3166-1 alpha-2, e.g., 'FR', 'JP', 'AU')"
    )


# Color-to-category mapping used by the API
_COLOR_CATEGORY: Dict[str, str] = {
    "green": "visa_free",
    "red": "visa_required",
    "blue": "visa_on_arrival",
    "light_blue": "evisa",
    "yellow": "evisa",
    "grey": "no_admission",
    "black": "no_admission",
}

# Label-to-category fallback (case-insensitive substring match)
_LABEL_CATEGORY: Dict[str, str] = {
    "visa free": "visa_free",
    "visa required": "visa_required",
    "visa on arrival": "visa_on_arrival",
    "e-visa": "evisa",
    "evisa": "evisa",
    "eta": "evisa",
    "no admission": "no_admission",
}


class VisaRequirementTool(BaseTravelAPITool):
    """Check visa requirements between countries."""

    name: str = "check_visa_requirements"
    description: str = """Check visa requirements for international travel between two countries.
    Input must include both origin country code (from_country) and destination country code (to_country)
    using ISO 3166-1 alpha-2 format (2-letter codes like 'US', 'GB', 'FR', 'JP').
    Returns visa requirement type, allowed duration of stay, and additional notes."""

    args_schema: type[BaseModel] = VisaRequirementInput

    api_name: str = "travelbuddy_visa"
    cache_prefix: str = "visa"

    BASE_URL: ClassVar[str] = "https://visa-requirement.p.rapidapi.com"

    _rapidapi_key: str = PrivateAttr(default="")

    @property
    def rapidapi_key(self) -> str:
        return self._rapidapi_key

    def __init__(self, **kwargs):
        """Initialize Visa tool with RapidAPI key from environment."""
        super().__init__(**kwargs)
        self._rapidapi_key = os.environ.get("PASSPORT_API_KEY") or ""

        if not self._rapidapi_key:
            raise ValueError(
                "PASSPORT_API_KEY not found in environment variables. "
                "Please sign up at https://rapidapi.com/ and add your key to .env: PASSPORT_API_KEY=your_key_here"
            )

    async def _call_api(self, **params) -> Dict[str, Any]:
        """Call visa requirement API via POST with JSON body."""
        from_country = params.get("from_country", "").upper()
        to_country = params.get("to_country", "").upper()

        if not from_country or not to_country:
            raise ValueError("Both from_country and to_country are required")

        if len(from_country) != 2 or len(to_country) != 2:
            raise ValueError(
                "Country codes must be 2-letter ISO 3166-1 alpha-2 codes. "
                "Examples: 'US' (USA), 'GB' (UK), 'FR' (France)"
            )

        headers = {
            "X-RapidAPI-Key": self._rapidapi_key,
            "X-RapidAPI-Host": "visa-requirement.p.rapidapi.com",
            "Content-Type": "application/json",
        }

        response = await self._make_request(
            "POST",
            f"{self.BASE_URL}/check",
            json={"passport": from_country, "destination": to_country},
            headers=headers,
        )

        return response.json()

    def _normalize_response(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize API response to standard format."""
        data = raw_data.get("data", {})

        passport = data.get("passport", {})
        destination = data.get("destination", {})
        visa_rules = data.get("visaRules", {})
        primary = visa_rules.get("primary", {})
        registrations = data.get("mandatoryRegistrations", [])

        from_code = passport.get("code", "").upper()
        to_code = destination.get("code", "").upper()

        label = primary.get("label", "")
        color = primary.get("color", "")
        duration_str = primary.get("duration", "")
        exception = primary.get("exception", "")
        evisa_link = primary.get("link")

        # Determine category: try color first, fall back to label
        category = _COLOR_CATEGORY.get(color.lower(), "unknown") if color else "unknown"
        if category == "unknown":
            label_lower = label.lower()
            for key, cat in _LABEL_CATEGORY.items():
                if key in label_lower:
                    category = cat
                    break

        duration_days = self._parse_duration(duration_str)
        summary = self._create_summary(category, duration_days, registrations)

        result = {
            "from_country": from_code,
            "to_country": to_code,
            "requirement": label,
            "category": category,
            "duration": duration_days,
            "exception": exception,
            "registrations": registrations,
            "summary": summary,
        }

        if evisa_link:
            result["evisa_link"] = evisa_link

        return result

    def _parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse duration string to integer days."""
        if not duration_str:
            return None

        numbers = re.findall(r'\d+', duration_str.lower())
        if not numbers:
            return None

        days = int(numbers[0])
        lower = duration_str.lower()
        if "month" in lower:
            days = days * 30
        elif "year" in lower:
            days = days * 365

        return days

    def _create_summary(self, category: str, duration: Optional[int], registrations: list) -> str:
        """Create human-readable summary."""
        has_reg = bool(registrations)
        reg_note = " Mandatory registration required." if has_reg else ""

        summaries = {
            "visa_free": (
                f"No visa required. Stay allowed for {duration} days.{reg_note}"
                if duration else f"No visa required.{reg_note}"
            ),
            "visa_on_arrival": (
                f"Visa on arrival available. Stay allowed for {duration} days.{reg_note}"
                if duration else f"Visa on arrival available.{reg_note}"
            ),
            "evisa": f"Electronic visa (eVisa) required. Apply online before travel.{reg_note}",
            "visa_required": f"Visa required before travel. Apply at embassy or consulate.{reg_note}",
            "no_admission": f"Travel not permitted or no admission allowed.{reg_note}",
            "unknown": f"Visa requirement: unknown.{reg_note}",
        }

        return summaries.get(category, f"Visa requirement: {category}.{reg_note}")


# Common country codes reference
COUNTRY_CODES: Dict[str, str] = {
    "United States": "US", "United Kingdom": "GB", "Canada": "CA",
    "Australia": "AU", "New Zealand": "NZ", "France": "FR",
    "Germany": "DE", "Italy": "IT", "Spain": "ES", "Netherlands": "NL",
    "Switzerland": "CH", "Austria": "AT", "Belgium": "BE", "Portugal": "PT",
    "Greece": "GR", "Japan": "JP", "China": "CN", "India": "IN",
    "Singapore": "SG", "Thailand": "TH", "South Korea": "KR",
    "Malaysia": "MY", "Indonesia": "ID", "Philippines": "PH", "Vietnam": "VN",
    "United Arab Emirates": "AE", "Saudi Arabia": "SA", "Turkey": "TR",
    "Israel": "IL", "Mexico": "MX", "Brazil": "BR", "Argentina": "AR",
    "Chile": "CL", "South Africa": "ZA", "Egypt": "EG", "Morocco": "MA",
    "Kenya": "KE", "Fiji": "FJ",
}


def get_country_code(country_name: str) -> Optional[str]:
    """Convert country name to 2-letter ISO code."""
    return COUNTRY_CODES.get(country_name)