"""
Currency conversion API tool using Frankfurter (no authentication required).

Frankfurter provides free currency exchange rates based on ECB data.
Free tier: Unlimited calls, 30+ currencies.
"""
from typing import Dict, Any, Optional, List, ClassVar
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from .base import BaseTravelAPITool


class CurrencyInput(BaseModel):
    """Input schema for currency conversion tool."""
    amount: float = Field(description="Amount to convert")
    from_currency: str = Field(description="Source currency code (e.g., USD, EUR)")
    to_currency: str = Field(description="Target currency code (e.g., JPY, GBP)")
    date: Optional[str] = Field(default=None, description="Historical date (YYYY-MM-DD), defaults to latest")


class CurrencyConversionTool(BaseTravelAPITool):
    """
    Convert currency using Frankfurter API (ECB exchange rates).
    
    Features:
    - No API key required
    - 30+ currencies supported
    - Latest and historical rates
    - Unlimited free usage
    """
    
    name: str = "currency_conversion"
    description: str = """Convert amount between currencies using real exchange rates.
    Input should include amount, from_currency code (e.g., USD), and to_currency code (e.g., EUR).
    Returns converted amount and exchange rate."""
    
    args_schema: type[BaseModel] = CurrencyInput
    
    api_name: str = "frankfurter"
    cache_prefix: str = "currency"
    
    BASE_URL: ClassVar[str] = "https://api.frankfurter.app"
    
    # Supported currencies
    SUPPORTED_CURRENCIES: ClassVar[set] = {
        "EUR", "USD", "JPY", "GBP", "CHF", "CAD", "AUD", "NZD",
        "CNY", "HKD", "SGD", "KRW", "INR", "MXN", "BRL", "ZAR",
        "SEK", "NOK", "DKK", "CZK", "PLN", "HUF", "RON", "BGN",
        "TRY", "ILS", "RUB", "THB", "MYR", "IDR", "PHP",
    }
    
    async def _call_api(self, **params) -> Dict[str, Any]:
        """
        Call Frankfurter API.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            date: Optional historical date
        
        Returns:
            Raw API response
        """
        amount = params.get("amount", 1.0)
        from_curr = params.get("from_currency", "USD").upper()
        to_curr = params.get("to_currency", "EUR").upper()
        date = params.get("date")
        
        # Validate currencies
        if from_curr not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {from_curr}")
        if to_curr not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {to_curr}")
        
        # Build URL
        if date:
            # Historical rate
            url = f"{self.BASE_URL}/{date}"
        else:
            # Latest rate
            url = f"{self.BASE_URL}/latest"
        
        # API parameters
        api_params = {
            "amount": amount,
            "from": from_curr,
            "to": to_curr,
        }
        
        response = await self._make_request("GET", url, params=api_params)
        return response.json()
    
    def _normalize_response(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Frankfurter response to standard format.
        
        Args:
            raw_data: Raw API response
        
        Returns:
            Normalized currency conversion data
        """
        amount = raw_data.get("amount")
        base = raw_data.get("base")
        date = raw_data.get("date")
        rates = raw_data.get("rates", {})
        
        # Get the converted amount
        to_currency = list(rates.keys())[0] if rates else "Unknown"
        converted_amount = rates.get(to_currency, 0)
        
        # Calculate exchange rate
        exchange_rate = converted_amount / amount if amount else 0
        
        return {
            "original_amount": amount,
            "original_currency": base,
            "converted_amount": converted_amount,
            "converted_currency": to_currency,
            "exchange_rate": exchange_rate,
            "rate_date": date,
            "formula": f"{amount} {base} × {exchange_rate:.4f} = {converted_amount:.2f} {to_currency}",
        }


class CurrencyListTool(BaseTravelAPITool):
    """
    List all available currencies from Frankfurter API.
    
    Simple tool to get supported currency codes and names.
    """
    
    name: str = "list_currencies"
    description: str = """List all available currency codes and names for conversion.
    No input required. Returns list of supported currencies."""
    
    api_name: str = "frankfurter"
    cache_prefix: str = "currency_list"
    
    BASE_URL: ClassVar[str] = "https://api.frankfurter.app"
    
    async def _call_api(self, **params) -> Dict[str, Any]:
        """
        Get list of currencies from Frankfurter.
        
        Returns:
            Raw API response with currency list
        """
        response = await self._make_request("GET", f"{self.BASE_URL}/currencies")
        return response.json()
    
    def _normalize_response(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize currency list response.
        
        Args:
            raw_data: Raw API response
        
        Returns:
            Normalized currency list
        """
        currencies = []
        for code, name in raw_data.items():
            currencies.append({
                "code": code,
                "name": name,
            })
        
        return {
            "currencies": currencies,
            "count": len(currencies),
        }
