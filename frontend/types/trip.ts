import type { Flight, Hotel, WeatherResult, CurrencyResult, VisaResult } from "./conversation";

export interface Trip {
  id: string;
  destination: string;
  startDate: string;
  endDate: string;
  budget?: { amount: number; currency: string };
  status: "draft" | "planned" | "completed";
  heroImageUrl?: string;
  createdAt: string;
}

export interface TripDetail extends Trip {
  days: TripDay[];
  flights?: Flight[];
  hotels?: Hotel[];
  weather?: WeatherResult;
  currency?: CurrencyResult;
  visa?: VisaResult;
}

export interface TripDay {
  date: string;
  activities: Activity[];
}

export interface Activity {
  time: string;
  title: string;
  description?: string;
  type:
    | "flight"
    | "hotel"
    | "restaurant"
    | "attraction"
    | "transport"
    | "free-time";
  cost?: { amount: number; currency: string };
}
