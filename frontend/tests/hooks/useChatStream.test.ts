import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useChatStream } from "@/hooks/useChatStream";
import { api } from "@/lib/api/client";
import { streamChat } from "@/lib/api/chat";
import type { Message } from "@/types";

vi.mock("@/lib/api/client");
vi.mock("@/lib/api/chat");

describe("useChatStream", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("loads existing messages on mount", async () => {
    const mockMessages: Message[] = [
      {
        id: "1",
        role: "user",
        content: "Hello",
        timestamp: "2026-01-01T00:00:00Z",
      },
      {
        id: "2",
        role: "assistant",
        content: "Hi there!",
        timestamp: "2026-01-01T00:00:01Z",
      },
    ];

    vi.mocked(api.getMessages).mockResolvedValue(mockMessages);

    const { result } = renderHook(() => useChatStream("conv-123"));

    // Initially loading
    expect(result.current.isLoading).toBe(true);
    expect(result.current.messages).toEqual([]);

    // Wait for messages to load
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.messages).toEqual(mockMessages);
    expect(api.getMessages).toHaveBeenCalledWith("conv-123");
  });

  it("sends user message and streams response", async () => {
    vi.mocked(api.getMessages).mockResolvedValue([]);

    // Mock streamChat to simulate streaming
    vi.mocked(streamChat).mockImplementation(
      async (
        _conversationId,
        _content,
        callbacks,
        _signal
      ): Promise<void> => {
        // Simulate streaming tokens
        callbacks.onToken?.("Hello");
        callbacks.onToken?.(" there");
        callbacks.onToken?.("!");

        // Simulate completion
        callbacks.onComplete?.("Hello there!", []);
      }
    );

    const { result } = renderHook(() => useChatStream("conv-123"));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Send a message
    await result.current.sendMessage("Hi");

    // Wait for streaming to complete
    await waitFor(() => {
      expect(result.current.isStreaming).toBe(false);
    });

    // Should have user message + assistant message
    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[0].role).toBe("user");
    expect(result.current.messages[0].content).toBe("Hi");
    expect(result.current.messages[1].role).toBe("assistant");
    expect(result.current.messages[1].content).toBe("Hello there!");
    expect(result.current.streamingContent).toBe("");
  });

  it("handles abort/stop streaming", async () => {
    vi.mocked(api.getMessages).mockResolvedValue([]);

    let abortSignal: AbortSignal | undefined;

    vi.mocked(streamChat).mockImplementation(
      async (
        _conversationId,
        _content,
        _callbacks,
        signal
      ): Promise<void> => {
        abortSignal = signal;
        // Simulate long-running stream that gets aborted
        return new Promise((_, reject) => {
          signal.addEventListener("abort", () => {
            reject(new DOMException("Aborted", "AbortError"));
          });
        });
      }
    );

    const { result } = renderHook(() => useChatStream("conv-123"));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Start sending a message
    const sendPromise = result.current.sendMessage("Test message");

    // Wait for streaming to start
    await waitFor(() => {
      expect(result.current.isStreaming).toBe(true);
    });

    // Stop streaming
    result.current.stopStreaming();

    await sendPromise;

    // Should no longer be streaming
    await waitFor(() => {
      expect(result.current.isStreaming).toBe(false);
    });
    expect(abortSignal?.aborted).toBe(true);
  });

  it("handles errors during streaming", async () => {
    vi.mocked(api.getMessages).mockResolvedValue([]);

    const errorMessage = "Network error occurred";

    vi.mocked(streamChat).mockImplementation(
      async (_conversationId, _content, callbacks): Promise<void> => {
        // Simulate error
        callbacks.onError?.(new Error(errorMessage));
      }
    );

    const { result } = renderHook(() => useChatStream("conv-123"));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Send a message
    await result.current.sendMessage("Test");

    // Should have error set
    await waitFor(() => {
      expect(result.current.error).toBe(errorMessage);
    });

    expect(result.current.isStreaming).toBe(false);
  });

  it("clears error when clearError is called", async () => {
    vi.mocked(api.getMessages).mockResolvedValue([]);

    vi.mocked(streamChat).mockImplementation(
      async (_conversationId, _content, callbacks): Promise<void> => {
        callbacks.onError?.(new Error("Test error"));
      }
    );

    const { result } = renderHook(() => useChatStream("conv-123"));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Trigger an error
    await result.current.sendMessage("Test");

    await waitFor(() => {
      expect(result.current.error).toBe("Test error");
    });

    // Clear the error
    result.current.clearError();

    await waitFor(() => {
      expect(result.current.error).toBe(null);
    });
  });
});
