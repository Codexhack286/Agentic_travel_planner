import type { Message } from "@/types";

export const mockUserMessage: Message = {
  id: "msg-1",
  role: "user",
  content: "Plan a 5-day trip to Tokyo",
  timestamp: "2025-01-15T10:30:00Z",
};

export const mockAssistantMessage: Message = {
  id: "msg-2",
  role: "assistant",
  content:
    "I'd love to help you plan a trip to **Tokyo**! Here's what I found:\n\n- Great weather in spring\n- Cherry blossom season in April\n\nLet me search for flights and hotels.",
  timestamp: "2025-01-15T10:30:05Z",
};

export const mockAssistantMessageWithTools: Message = {
  id: "msg-3",
  role: "assistant",
  content: "Here are the flight options I found:",
  toolResults: [
    {
      type: "flight",
      data: {
        flights: [
          {
            airline: "ANA",
            flightNumber: "NH10",
            departure: "2025-04-01T08:00:00Z",
            arrival: "2025-04-02T12:00:00Z",
            duration: "PT14H",
            stops: 0,
            price: { amount: 850, currency: "USD" },
          },
        ],
        origin: "JFK",
        destination: "NRT",
        departureDate: "2025-04-01",
      },
    },
  ],
  timestamp: "2025-01-15T10:30:10Z",
};

export const mockMessages: Message[] = [
  mockUserMessage,
  mockAssistantMessage,
  mockAssistantMessageWithTools,
];
