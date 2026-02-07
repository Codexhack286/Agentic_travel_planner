// API request types
export interface ChatRequest {
  conversation_id: string;
  message: string;
}

export interface CreateConversationRequest {
  title?: string;
}

// API response types
export interface HealthResponse {
  status: "ok" | "degraded" | "down";
  version?: string;
  llm_provider?: string;
}

// SSE event types
export interface SSETokenEvent {
  type: "token";
  content: string;
}

export interface SSEToolResultEvent {
  type: "tool_result";
  content: {
    type: string;
    data: Record<string, unknown>;
  };
}

export interface SSECompleteEvent {
  type: "complete";
  content: {
    role: "assistant";
    content: string;
    toolResults?: Array<{
      type: string;
      data: Record<string, unknown>;
    }>;
  };
}

export interface SSEErrorEvent {
  type: "error";
  content: string;
}

export type SSEEvent =
  | SSETokenEvent
  | SSEToolResultEvent
  | SSECompleteEvent
  | SSEErrorEvent;

// API error
export class ApiError extends Error {
  constructor(
    public status: number,
    public body: string
  ) {
    super(`API Error ${status}: ${body}`);
    this.name = "ApiError";
  }
}
