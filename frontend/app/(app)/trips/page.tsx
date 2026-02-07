"use client";

import { Map } from "lucide-react";
import { EmptyState } from "@/components/EmptyState";

export default function TripsPage() {
  return (
    <EmptyState
      icon={Map}
      title="Trip Dashboard"
      description="Your saved trip plans will appear here. Start a chat to plan your next adventure!"
      action={{
        label: "Start planning",
        onClick: () => (window.location.href = "/chat"),
      }}
    />
  );
}
