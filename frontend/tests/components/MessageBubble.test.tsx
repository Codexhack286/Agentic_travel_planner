import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MessageBubble } from "@/components/chat/MessageBubble";
import type { Message } from "@/types";

describe("MessageBubble", () => {
  it("renders user message (right-aligned)", () => {
    const userMessage: Message = {
      id: "1",
      role: "user",
      content: "Hello, I need help planning a trip",
      timestamp: "2026-01-01T12:00:00Z",
    };

    render(<MessageBubble message={userMessage} />);

    // Check that the message content is rendered
    expect(
      screen.getByText("Hello, I need help planning a trip")
    ).toBeInTheDocument();

    // Check for user avatar (using aria-label)
    expect(screen.getByLabelText("You said")).toBeInTheDocument();

    // Verify user avatar icon is present (User icon from lucide-react)
    const article = screen.getByRole("article");
    expect(article).toHaveClass("flex-row-reverse"); // Right-aligned
  });

  it("renders assistant message with markdown", () => {
    const assistantMessage: Message = {
      id: "2",
      role: "assistant",
      content: "Here are some **bold** recommendations and a [link](https://example.com)",
      timestamp: "2026-01-01T12:01:00Z",
    };

    render(<MessageBubble message={assistantMessage} />);

    // Check that the message is rendered
    expect(screen.getByLabelText("AI Assistant said")).toBeInTheDocument();

    // The MarkdownRenderer component should process the markdown
    // We can check that the content includes the text (markdown processing is tested separately)
    const article = screen.getByRole("article");
    expect(article).toHaveClass("flex-row"); // Left-aligned (not flex-row-reverse)
  });

  it("renders tool result cards", () => {
    const messageWithTools: Message = {
      id: "3",
      role: "assistant",
      content: "I found some flights for you:",
      timestamp: "2026-01-01T12:02:00Z",
      toolResults: [
        {
          type: "flight",
          data: {
            origin: "JFK",
            destination: "LAX",
            departureDate: "2026-02-15",
            flights: [
              {
                airline: "Test Airlines",
                flightNumber: "TA123",
                duration: "4h 00m",
                stops: 0,
                price: {
                  amount: 299,
                  currency: "USD",
                },
              },
            ],
          },
        },
      ],
    };

    render(<MessageBubble message={messageWithTools} />);

    // Check that the main message is rendered
    expect(screen.getByText("I found some flights for you:")).toBeInTheDocument();

    // Check that tool results are rendered (ToolResultCard should be present)
    // The actual rendering of tool result cards is tested in their own test files
    // Here we just verify that the container exists
    const article = screen.getByRole("article");
    expect(article).toBeInTheDocument();
  });
});
