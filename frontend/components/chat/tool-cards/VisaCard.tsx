"use client";

import { Shield, CheckCircle, AlertCircle, Clock, XCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { VisaResult, ToolResultData } from "@/types";

interface VisaCardProps {
  data: ToolResultData;
}

const requirementConfig = {
  "visa-free": {
    icon: CheckCircle,
    label: "Visa Free",
    color: "text-green-600 dark:text-green-400",
    bg: "bg-green-50 dark:bg-green-950/30",
  },
  "visa-on-arrival": {
    icon: Clock,
    label: "Visa on Arrival",
    color: "text-blue-600 dark:text-blue-400",
    bg: "bg-blue-50 dark:bg-blue-950/30",
  },
  "e-visa": {
    icon: AlertCircle,
    label: "e-Visa Required",
    color: "text-yellow-600 dark:text-yellow-400",
    bg: "bg-yellow-50 dark:bg-yellow-950/30",
  },
  "visa-required": {
    icon: XCircle,
    label: "Visa Required",
    color: "text-red-600 dark:text-red-400",
    bg: "bg-red-50 dark:bg-red-950/30",
  },
};

export function VisaCard({ data }: VisaCardProps) {
  const visaData = data as VisaResult;
  const config = requirementConfig[visaData.requirement];
  const StatusIcon = config.icon;

  return (
    <Card className="border-visa/20">
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <Shield className="h-4 w-4 text-visa" />
          <CardTitle className="text-sm">
            Visa: {visaData.from} → {visaData.to}
          </CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div
          className={cn(
            "flex items-center gap-3 rounded-lg p-3",
            config.bg
          )}
        >
          <StatusIcon className={cn("h-6 w-6", config.color)} />
          <div>
            <p className={cn("font-semibold", config.color)}>
              {config.label}
            </p>
            {visaData.duration && (
              <p className="text-sm text-muted-foreground">
                Duration: {visaData.duration}
              </p>
            )}
          </div>
        </div>
        {visaData.notes && (
          <p className="mt-2 text-xs text-muted-foreground">
            {visaData.notes}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
