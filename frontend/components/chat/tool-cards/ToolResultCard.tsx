"use client";

import type { ToolType, ToolResultData } from "@/types";
import { FlightCard } from "./FlightCard";
import { HotelCard } from "./HotelCard";
import { WeatherCard } from "./WeatherCard";
import { CurrencyCard } from "./CurrencyCard";
import { DestinationCard } from "./DestinationCard";
import { VisaCard } from "./VisaCard";

interface ToolResultCardProps {
  type: ToolType;
  data: ToolResultData;
}

export function ToolResultCard({ type, data }: ToolResultCardProps) {
  switch (type) {
    case "flight":
      return <FlightCard data={data} />;
    case "hotel":
      return <HotelCard data={data} />;
    case "weather":
      return <WeatherCard data={data} />;
    case "currency":
      return <CurrencyCard data={data} />;
    case "destination":
      return <DestinationCard data={data} />;
    case "visa":
      return <VisaCard data={data} />;
    default:
      return (
        <div className="rounded-lg border bg-muted/50 p-3 text-sm text-muted-foreground">
          Unknown tool result: {type}
        </div>
      );
  }
}
