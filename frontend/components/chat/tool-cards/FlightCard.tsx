"use client";

import { Plane, Clock, ArrowRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatCurrency, formatDuration } from "@/lib/format";
import type { FlightResult, ToolResultData } from "@/types";

interface FlightCardProps {
  data: ToolResultData;
}

export function FlightCard({ data }: FlightCardProps) {
  const flightData = data as FlightResult;

  return (
    <Card className="border-flight/20 bg-flight/5">
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <Plane className="h-4 w-4 text-flight" />
          <CardTitle className="text-sm">
            Flights: {flightData.origin} <ArrowRight className="inline h-3 w-3" />{" "}
            {flightData.destination}
          </CardTitle>
          <Badge variant="flight" className="ml-auto">
            {flightData.departureDate}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        {flightData.flights.slice(0, 3).map((flight, idx) => (
          <div
            key={idx}
            className="flex items-center justify-between rounded-lg bg-background/60 p-2.5 text-sm"
          >
            <div className="space-y-0.5">
              <p className="font-medium">
                {flight.airline} {flight.flightNumber}
              </p>
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                {formatDuration(flight.duration)}
                {flight.stops > 0 && (
                  <span className="ml-1">
                    · {flight.stops} stop{flight.stops > 1 ? "s" : ""}
                  </span>
                )}
              </div>
            </div>
            <p className="text-lg font-bold text-flight">
              {formatCurrency(flight.price.amount, flight.price.currency)}
            </p>
          </div>
        ))}
        {flightData.flights.length > 3 && (
          <p className="text-xs text-muted-foreground text-center">
            +{flightData.flights.length - 3} more options
          </p>
        )}
      </CardContent>
    </Card>
  );
}
