"use client";

import { Settings } from "lucide-react";
import { EmptyState } from "@/components/EmptyState";

export default function SettingsPage() {
  return (
    <EmptyState
      icon={Settings}
      title="Settings"
      description="User preferences like budget range, travel style, and dietary preferences will be available here in a future update."
    />
  );
}
