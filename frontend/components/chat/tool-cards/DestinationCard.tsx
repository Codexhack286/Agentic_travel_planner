"use client";

import Image from "next/image";
import { MapPin, Globe, Clock, Users } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { DestinationResult, ToolResultData } from "@/types";

interface DestinationCardProps {
  data: ToolResultData;
}

export function DestinationCard({ data }: DestinationCardProps) {
  const destData = data as DestinationResult;

  return (
    <Card className="border-destination/20 overflow-hidden">
      {/* Hero image */}
      {destData.imageUrl && (
        <div className="relative h-40 w-full">
          <Image
            src={destData.imageUrl}
            alt={`${destData.name} destination`}
            fill
            className="object-cover"
            sizes="(max-width: 768px) 100vw, 600px"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
          <div className="absolute bottom-3 left-4 text-white">
            <h3 className="text-xl font-bold">
              {destData.flag} {destData.name}
            </h3>
            <p className="text-sm opacity-90">Capital: {destData.capital}</p>
          </div>
          {destData.imageAttribution && (
            <p className="absolute bottom-1 right-2 text-[10px] text-white/60">
              Photo: {destData.imageAttribution}
            </p>
          )}
        </div>
      )}

      {!destData.imageUrl && (
        <CardHeader className="bg-destination/5 pb-2">
          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-destination" />
            <CardTitle className="text-sm">
              {destData.flag} {destData.name}
            </CardTitle>
          </div>
        </CardHeader>
      )}

      <CardContent className="grid grid-cols-2 gap-3 p-4">
        <InfoItem icon={Globe} label="Language" value={destData.language.join(", ")} />
        <InfoItem icon={Clock} label="Timezone" value={destData.timezone[0] || "N/A"} />
        <InfoItem
          icon={MapPin}
          label="Currency"
          value={`${destData.currency.name} (${destData.currency.symbol})`}
        />
        <InfoItem
          icon={Users}
          label="Population"
          value={formatPopulation(destData.population)}
        />
      </CardContent>
    </Card>
  );
}

function InfoItem({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-start gap-2">
      <Icon className="mt-0.5 h-3.5 w-3.5 shrink-0 text-muted-foreground" />
      <div>
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="text-sm font-medium">{value}</p>
      </div>
    </div>
  );
}

function formatPopulation(pop: number): string {
  if (pop >= 1_000_000_000) return `${(pop / 1_000_000_000).toFixed(1)}B`;
  if (pop >= 1_000_000) return `${(pop / 1_000_000).toFixed(1)}M`;
  if (pop >= 1_000) return `${(pop / 1_000).toFixed(0)}K`;
  return pop.toString();
}
