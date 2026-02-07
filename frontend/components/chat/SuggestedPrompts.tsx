"use client";

import {
  Plane,
  CloudSun,
  PlaneTakeoff,
  Banknote,
  MapPin,
  GitCompare,
  type LucideIcon,
} from "lucide-react";
import { SUGGESTED_PROMPTS } from "@/lib/constants";

const iconMap: Record<string, LucideIcon> = {
  plane: Plane,
  "cloud-sun": CloudSun,
  "plane-takeoff": PlaneTakeoff,
  banknote: Banknote,
  "map-pin": MapPin,
  "git-compare": GitCompare,
};

interface SuggestedPromptsProps {
  onSelect: (prompt: string) => void;
}

export function SuggestedPrompts({ onSelect }: SuggestedPromptsProps) {
  return (
    <div className="mx-auto max-w-2xl px-4">
      <div className="mb-8 text-center">
        <h2 className="text-2xl font-bold tracking-tight">
          Where do you want to go?
        </h2>
        <p className="mt-2 text-muted-foreground">
          Ask me about flights, hotels, weather, visas, or let me plan your
          entire trip.
        </p>
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {SUGGESTED_PROMPTS.map((item) => {
          const Icon = iconMap[item.icon] || MapPin;
          return (
            <button
              key={item.title}
              onClick={() => onSelect(item.prompt)}
              className="flex items-start gap-3 rounded-xl border bg-card p-4 text-left transition-colors hover:bg-muted"
            >
              <div className="mt-0.5 rounded-lg bg-primary/10 p-2">
                <Icon className="h-4 w-4 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm">{item.title}</p>
                <p className="text-xs text-muted-foreground line-clamp-2 mt-0.5">
                  {item.prompt}
                </p>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
