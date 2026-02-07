"use client";

import { CloudSun, Thermometer } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatTemperature } from "@/lib/format";
import type { WeatherResult, ToolResultData } from "@/types";

interface WeatherCardProps {
  data: ToolResultData;
}

export function WeatherCard({ data }: WeatherCardProps) {
  const weatherData = data as WeatherResult;

  return (
    <Card className="border-weather/20 bg-weather/5">
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <CloudSun className="h-4 w-4 text-weather" />
          <CardTitle className="text-sm">
            Weather in {weatherData.location}
          </CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        {/* Current weather */}
        <div className="mb-3 flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Thermometer className="h-5 w-5 text-weather" />
            <span className="text-2xl font-bold">
              {formatTemperature(
                weatherData.current.temp,
                weatherData.unit
              )}
            </span>
          </div>
          <Badge variant="weather">{weatherData.current.condition}</Badge>
        </div>

        {/* Forecast */}
        {weatherData.forecast.length > 0 && (
          <div className="flex gap-2 overflow-x-auto pb-1">
            {weatherData.forecast.slice(0, 5).map((day) => (
              <div
                key={day.date}
                className="flex min-w-[72px] flex-col items-center rounded-lg bg-background/60 p-2 text-xs"
              >
                <span className="font-medium">
                  {new Date(day.date).toLocaleDateString("en-US", {
                    weekday: "short",
                  })}
                </span>
                <span className="my-1 text-base">{day.icon}</span>
                <span className="font-semibold">
                  {formatTemperature(day.high, weatherData.unit)}
                </span>
                <span className="text-muted-foreground">
                  {formatTemperature(day.low, weatherData.unit)}
                </span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
