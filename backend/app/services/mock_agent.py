import asyncio
import json
import re
from typing import AsyncGenerator


MOCK_RESPONSES = {
    "flight": {
        "text": "I found some great flight options for you! Here are the top results based on your search criteria:\n\n**Best Overall:** ANA flight NH10 offers a direct route with excellent service.\n\n**Budget Pick:** JAL flight JL5 has a layover but saves you over $100.",
        "tool_result": {
            "type": "flight",
            "data": {
                "flights": [
                    {
                        "airline": "ANA",
                        "flightNumber": "NH10",
                        "departure": "2025-04-01T08:00:00Z",
                        "arrival": "2025-04-02T12:00:00Z",
                        "duration": "PT14H",
                        "stops": 0,
                        "price": {"amount": 850, "currency": "USD"},
                    },
                    {
                        "airline": "JAL",
                        "flightNumber": "JL5",
                        "departure": "2025-04-01T10:30:00Z",
                        "arrival": "2025-04-02T15:30:00Z",
                        "duration": "PT15H",
                        "stops": 1,
                        "price": {"amount": 720, "currency": "USD"},
                    },
                    {
                        "airline": "United",
                        "flightNumber": "UA79",
                        "departure": "2025-04-01T13:00:00Z",
                        "arrival": "2025-04-02T17:45:00Z",
                        "duration": "PT14H45M",
                        "stops": 0,
                        "price": {"amount": 790, "currency": "USD"},
                    },
                ],
                "origin": "JFK",
                "destination": "NRT",
                "departureDate": "2025-04-01",
            },
        },
    },
    "weather": {
        "text": "Here's the current weather forecast for your destination. Looks like you'll have mostly pleasant weather!\n\n**Current conditions:** Partly cloudy with comfortable temperatures.\n\nPack layers — mornings and evenings can be cool.",
        "tool_result": {
            "type": "weather",
            "data": {
                "location": "Tokyo, Japan",
                "current": {"temp": 18, "condition": "Partly Cloudy", "icon": "partly-cloudy"},
                "forecast": [
                    {"date": "2025-04-01", "high": 20, "low": 12, "condition": "Sunny", "icon": "sunny"},
                    {"date": "2025-04-02", "high": 18, "low": 10, "condition": "Cloudy", "icon": "cloudy"},
                    {"date": "2025-04-03", "high": 22, "low": 14, "condition": "Sunny", "icon": "sunny"},
                    {"date": "2025-04-04", "high": 17, "low": 11, "condition": "Rain", "icon": "rain"},
                    {"date": "2025-04-05", "high": 19, "low": 12, "condition": "Partly Cloudy", "icon": "partly-cloudy"},
                ],
                "unit": "celsius",
            },
        },
    },
    "hotel": {
        "text": "I've found several excellent hotels for your stay. Here are my top picks:\n\n**Luxury:** Park Hyatt Tokyo — iconic views, world-class service.\n\n**Mid-Range:** Hotel Gracery Shinjuku — great location, Godzilla on the roof!",
        "tool_result": {
            "type": "hotel",
            "data": {
                "hotels": [
                    {
                        "name": "Park Hyatt Tokyo",
                        "rating": 5,
                        "pricePerNight": {"amount": 450, "currency": "USD"},
                        "address": "3-7-1-2 Nishi-Shinjuku, Shinjuku",
                        "amenities": ["WiFi", "Pool", "Spa", "Restaurant"],
                    },
                    {
                        "name": "Hotel Gracery Shinjuku",
                        "rating": 4,
                        "pricePerNight": {"amount": 150, "currency": "USD"},
                        "address": "1-19-1 Kabukicho, Shinjuku",
                        "amenities": ["WiFi", "Restaurant"],
                    },
                ],
                "destination": "Tokyo",
                "checkIn": "2025-04-01",
                "checkOut": "2025-04-06",
            },
        },
    },
    "default": {
        "text": "That's a great question! Let me help you with your travel planning.\n\nI can assist with:\n- **Flight search** — finding the best routes and prices\n- **Hotel booking** — accommodations that match your style\n- **Weather forecasts** — so you pack the right clothes\n- **Currency conversion** — know your budget in local currency\n- **Destination info** — culture, language, timezone\n- **Visa requirements** — entry rules for your nationality\n\nWhat would you like to explore first?",
        "tool_result": None,
    },
}


def _detect_intent(message: str) -> str:
    msg = message.lower()
    if any(w in msg for w in ["flight", "fly", "airplane", "airport"]):
        return "flight"
    if any(w in msg for w in ["weather", "forecast", "temperature", "rain"]):
        return "weather"
    if any(w in msg for w in ["hotel", "stay", "accommodation", "room"]):
        return "hotel"
    return "default"


async def generate_mock_response(message: str) -> AsyncGenerator[str, None]:
    """Stream a mock agent response as SSE events."""
    intent = _detect_intent(message)
    response = MOCK_RESPONSES[intent]
    text = response["text"]
    tool_result = response["tool_result"]

    # Stream text tokens word by word
    words = text.split(" ")
    for word in words:
        token = word + " "
        event = json.dumps({"type": "token", "content": token})
        yield f"data: {event}\n\n"
        await asyncio.sleep(0.04)

    # Send tool result if available
    if tool_result:
        event = json.dumps({"type": "tool_result", "content": tool_result})
        yield f"data: {event}\n\n"
        await asyncio.sleep(0.1)

    # Send complete event
    complete_content = {
        "role": "assistant",
        "content": text,
    }
    if tool_result:
        complete_content["toolResults"] = [tool_result]

    event = json.dumps({"type": "complete", "content": complete_content})
    yield f"data: {event}\n\n"
    yield "data: [DONE]\n\n"
