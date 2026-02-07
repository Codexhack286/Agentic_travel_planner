import type { ToolResult } from "@/types";

export const mockFlightResult: ToolResult = {
  type: "flight",
  data: {
    flights: [
      {
        airline: "ANA",
        flightNumber: "NH10",
        departure: "2025-04-01T08:00:00Z",
        arrival: "2025-04-02T12:00:00Z",
        duration: "PT14H",
        stops: 0,
        price: { amount: 850, currency: "USD" },
      },
      {
        airline: "JAL",
        flightNumber: "JL5",
        departure: "2025-04-01T10:30:00Z",
        arrival: "2025-04-02T15:30:00Z",
        duration: "PT15H",
        stops: 1,
        price: { amount: 720, currency: "USD" },
      },
    ],
    origin: "JFK",
    destination: "NRT",
    departureDate: "2025-04-01",
  },
};

export const mockHotelResult: ToolResult = {
  type: "hotel",
  data: {
    hotels: [
      {
        name: "Park Hyatt Tokyo",
        rating: 5,
        pricePerNight: { amount: 450, currency: "USD" },
        address: "3-7-1-2 Nishi-Shinjuku, Shinjuku",
        amenities: ["WiFi", "Pool", "Spa", "Restaurant"],
      },
    ],
    destination: "Tokyo",
    checkIn: "2025-04-01",
    checkOut: "2025-04-06",
  },
};

export const mockWeatherResult: ToolResult = {
  type: "weather",
  data: {
    location: "Tokyo, Japan",
    current: { temp: 18, condition: "Partly Cloudy", icon: "partly-cloudy" },
    forecast: [
      {
        date: "2025-04-01",
        high: 20,
        low: 12,
        condition: "Sunny",
        icon: "sunny",
      },
      {
        date: "2025-04-02",
        high: 18,
        low: 10,
        condition: "Cloudy",
        icon: "cloudy",
      },
    ],
    unit: "celsius" as const,
  },
};

export const mockCurrencyResult: ToolResult = {
  type: "currency",
  data: {
    from: "USD",
    to: "JPY",
    rate: 149.5,
    amount: 1000,
    convertedAmount: 149500,
    lastUpdated: "2025-01-15T10:00:00Z",
  },
};

export const mockDestinationResult: ToolResult = {
  type: "destination",
  data: {
    name: "Japan",
    capital: "Tokyo",
    language: ["Japanese"],
    timezone: ["Asia/Tokyo"],
    currency: { name: "Japanese Yen", code: "JPY", symbol: "¥" },
    population: 125800000,
    flag: "🇯🇵",
    imageUrl: "https://images.unsplash.com/photo-example",
    imageAttribution: "Photo by John Doe on Unsplash",
  },
};

export const mockVisaResult: ToolResult = {
  type: "visa",
  data: {
    from: "United States",
    to: "Japan",
    requirement: "visa-free" as const,
    duration: "90 days",
    notes: "Valid passport required with at least 6 months validity.",
  },
};
