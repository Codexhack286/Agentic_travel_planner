export interface Conversation {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  metadata?: Record<string, unknown>;
}

export interface Message {
  id?: string;
  role: "user" | "assistant" | "tool";
  content: string;
  toolCalls?: ToolCall[];
  toolResults?: ToolResult[];
  timestamp: string;
}

export interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
}

export interface ToolResult {
  type: ToolType;
  data: ToolResultData;
}

export type ToolType =
  | "flight"
  | "hotel"
  | "weather"
  | "currency"
  | "destination"
  | "visa";

export type ToolResultData =
  | FlightResult
  | HotelResult
  | WeatherResult
  | CurrencyResult
  | DestinationResult
  | VisaResult;

// Flight types
export interface FlightResult {
  flights: Flight[];
  origin: string;
  destination: string;
  departureDate: string;
}

export interface Flight {
  airline: string;
  flightNumber: string;
  departure: string;
  arrival: string;
  duration: string;
  stops: number;
  price: { amount: number; currency: string };
}

// Hotel types
export interface HotelResult {
  hotels: Hotel[];
  destination: string;
  checkIn: string;
  checkOut: string;
}

export interface Hotel {
  name: string;
  rating: number;
  pricePerNight: { amount: number; currency: string };
  address?: string;
  amenities?: string[];
}

// Weather types
export interface WeatherResult {
  location: string;
  current: { temp: number; condition: string; icon: string };
  forecast: Array<{
    date: string;
    high: number;
    low: number;
    condition: string;
    icon: string;
  }>;
  unit: "celsius" | "fahrenheit";
}

// Currency types
export interface CurrencyResult {
  from: string;
  to: string;
  rate: number;
  amount?: number;
  convertedAmount?: number;
  lastUpdated: string;
}

// Destination types
export interface DestinationResult {
  name: string;
  capital: string;
  language: string[];
  timezone: string[];
  currency: { name: string; code: string; symbol: string };
  population: number;
  flag: string;
  imageUrl?: string;
  imageAttribution?: string;
}

// Visa types
export interface VisaResult {
  from: string;
  to: string;
  requirement: "visa-free" | "visa-on-arrival" | "e-visa" | "visa-required";
  duration?: string;
  notes?: string;
}
