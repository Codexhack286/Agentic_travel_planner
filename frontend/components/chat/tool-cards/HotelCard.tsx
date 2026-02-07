"use client";

import { Hotel, Star } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatCurrency } from "@/lib/format";
import type { HotelResult, ToolResultData } from "@/types";

interface HotelCardProps {
  data: ToolResultData;
}

export function HotelCard({ data }: HotelCardProps) {
  const hotelData = data as HotelResult;

  return (
    <Card className="border-hotel/20 bg-hotel/5">
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <Hotel className="h-4 w-4 text-hotel" />
          <CardTitle className="text-sm">
            Hotels in {hotelData.destination}
          </CardTitle>
          <Badge variant="hotel" className="ml-auto">
            {hotelData.checkIn} - {hotelData.checkOut}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        {hotelData.hotels.slice(0, 3).map((hotel, idx) => (
          <div
            key={idx}
            className="flex items-center justify-between rounded-lg bg-background/60 p-2.5 text-sm"
          >
            <div className="space-y-0.5">
              <p className="font-medium">{hotel.name}</p>
              <div className="flex items-center gap-0.5">
                {Array.from({ length: hotel.rating }).map((_, i) => (
                  <Star
                    key={i}
                    className="h-3 w-3 fill-hotel text-hotel"
                  />
                ))}
              </div>
            </div>
            <div className="text-right">
              <p className="text-lg font-bold text-hotel">
                {formatCurrency(
                  hotel.pricePerNight.amount,
                  hotel.pricePerNight.currency
                )}
              </p>
              <p className="text-xs text-muted-foreground">/night</p>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
