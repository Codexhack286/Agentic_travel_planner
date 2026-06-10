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
import { cn } from "@/lib/utils";

const iconMap: Record<string, LucideIcon> = {
  plane: Plane,
  "cloud-sun": CloudSun,
  "plane-takeoff": PlaneTakeoff,
  banknote: Banknote,
  "map-pin": MapPin,
  "git-compare": GitCompare,
};

// Premium themed color palettes for each suggested action type
const colorMap: Record<string, { bg: string; text: string; border: string; hoverBg: string }> = {
  plane: { 
    bg: "bg-sky-500/10 dark:bg-sky-500/15", 
    text: "text-sky-600 dark:text-sky-400", 
    border: "hover:border-sky-500/30", 
    hoverBg: "hover:bg-sky-500/[0.02]" 
  },
  "cloud-sun": { 
    bg: "bg-amber-500/10 dark:bg-amber-500/15", 
    text: "text-amber-600 dark:text-amber-400", 
    border: "hover:border-amber-500/30", 
    hoverBg: "hover:bg-amber-500/[0.02]" 
  },
  "plane-takeoff": { 
    bg: "bg-indigo-500/10 dark:bg-indigo-500/15", 
    text: "text-indigo-600 dark:text-indigo-400", 
    border: "hover:border-indigo-500/30", 
    hoverBg: "hover:bg-indigo-500/[0.02]" 
  },
  banknote: { 
    bg: "bg-emerald-500/10 dark:bg-emerald-500/15", 
    text: "text-emerald-600 dark:text-emerald-400", 
    border: "hover:border-emerald-500/30", 
    hoverBg: "hover:bg-emerald-500/[0.02]" 
  },
  "map-pin": { 
    bg: "bg-rose-500/10 dark:bg-rose-500/15", 
    text: "text-rose-600 dark:text-rose-400", 
    border: "hover:border-rose-500/30", 
    hoverBg: "hover:bg-rose-500/[0.02]" 
  },
  "git-compare": { 
    bg: "bg-violet-500/10 dark:bg-violet-500/15", 
    text: "text-violet-600 dark:text-violet-400", 
    border: "hover:border-violet-500/30", 
    hoverBg: "hover:bg-violet-500/[0.02]" 
  },
};

interface SuggestedPromptsProps {
  onSelect: (prompt: string) => void;
}

export function SuggestedPrompts({ onSelect }: SuggestedPromptsProps) {
  return (
    <div className="mx-auto max-w-2xl px-6 py-10 bg-mesh border border-primary/5 rounded-3xl shadow-sm">
      <div className="mb-10 text-center">
        <h2 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-primary via-primary/90 to-accent bg-clip-text text-transparent">
          Where do you want to go?
        </h2>
        <p className="mt-3 text-sm text-muted-foreground max-w-md mx-auto leading-relaxed">
          Ask me about flights, hotels, weather, visas, or let me plan your
          entire trip dynamically.
        </p>
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {SUGGESTED_PROMPTS.map((item) => {
          const Icon = iconMap[item.icon] || MapPin;
          const colors = colorMap[item.icon] || {
            bg: "bg-primary/10",
            text: "text-primary",
            border: "hover:border-primary/30",
            hoverBg: "hover:bg-primary/[0.02]",
          };
          
          return (
            <button
              key={item.title}
              onClick={() => onSelect(item.prompt)}
              className={cn(
                "flex items-start gap-4 rounded-2xl border bg-card/60 backdrop-blur-sm p-4 text-left transition-all duration-300 ease-out",
                "hover:-translate-y-1 hover:shadow-lg hover:shadow-primary/5",
                colors.border,
                colors.hoverBg
              )}
            >
              <div className={cn("mt-0.5 rounded-xl p-2.5 shrink-0 transition-transform duration-300 group-hover:scale-110", colors.bg)}>
                <Icon className={cn("h-5 w-5", colors.text)} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-sm text-foreground transition-colors">{item.title}</p>
                <p className="text-xs text-muted-foreground line-clamp-2 mt-1 leading-relaxed">
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
