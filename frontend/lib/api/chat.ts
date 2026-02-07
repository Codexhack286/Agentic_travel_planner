import type { ToolResult } from "@/types";
import type { SSEEvent } from "./types";
import { ApiError } from "./types";
import { API_BASE_URL } from "@/lib/constants";

export interface StreamChatCallbacks {
  onToken: (token: string) => void;
  onToolResult: (toolResult: ToolResult) => void;
  onComplete: (content: string, toolResults: ToolResult[]) => void;
  onError: (error: Error) => void;
}

export async function streamChat(
  conversationId: string,
  message: string,
  callbacks: StreamChatCallbacks,
  signal?: AbortSignal
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      conversation_id: conversationId,
      message,
    }),
    signal,
  });

  if (!response.ok) {
    throw new ApiError(response.status, await response.text());
  }

  if (!response.body) {
    throw new Error("Response body is null");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  const toolResults: ToolResult[] = [];

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;

        const rawData = line.slice(6).trim();
        if (rawData === "[DONE]") return;

        try {
          const event: SSEEvent = JSON.parse(rawData);

          switch (event.type) {
            case "token":
              callbacks.onToken(event.content);
              break;
            case "tool_result":
              const toolResult = event.content as unknown as ToolResult;
              toolResults.push(toolResult);
              callbacks.onToolResult(toolResult);
              break;
            case "complete":
              callbacks.onComplete(event.content.content, toolResults);
              break;
            case "error":
              callbacks.onError(new Error(event.content));
              break;
          }
        } catch {
          // Skip malformed SSE events
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
