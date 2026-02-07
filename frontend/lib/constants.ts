export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const SUGGESTED_PROMPTS = [
  {
    title: "Plan a trip",
    prompt: "Plan a 5-day trip to Tokyo, Japan for 2 travelers on a moderate budget",
    icon: "plane" as const,
  },
  {
    title: "Check weather",
    prompt: "What's the weather forecast for Barcelona next week?",
    icon: "cloud-sun" as const,
  },
  {
    title: "Find flights",
    prompt: "Find flights from New York to London departing next month",
    icon: "plane-takeoff" as const,
  },
  {
    title: "Convert currency",
    prompt: "Convert 1000 USD to EUR and JPY",
    icon: "banknote" as const,
  },
  {
    title: "Destination info",
    prompt: "Tell me about visiting Thailand - visa requirements, currency, language, and best time to visit",
    icon: "map-pin" as const,
  },
  {
    title: "Compare destinations",
    prompt: "Compare Paris and Rome for a romantic spring getaway",
    icon: "git-compare" as const,
  },
] as const;

export const MAX_MESSAGE_LENGTH = 2000;
export const BACKEND_WAKE_TIMEOUT_MS = 5000;
