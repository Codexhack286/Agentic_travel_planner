import type { Conversation, Message } from "@/types";
import type { HealthResponse, CreateConversationRequest } from "./types";
import { ApiError } from "./types";
import { API_BASE_URL } from "@/lib/constants";

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  private async request<T>(path: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new ApiError(response.status, await response.text());
    }

    return response.json();
  }

  // Conversations
  async getConversations(): Promise<Conversation[]> {
    return this.request<Conversation[]>("/api/conversations");
  }

  async getConversation(id: string): Promise<Conversation> {
    return this.request<Conversation>(`/api/conversations/${id}`);
  }

  async createConversation(
    data?: CreateConversationRequest
  ): Promise<Conversation> {
    return this.request<Conversation>("/api/conversations", {
      method: "POST",
      body: JSON.stringify(data || {}),
    });
  }

  async updateConversation(
    id: string,
    data: Partial<Pick<Conversation, "title">>
  ): Promise<Conversation> {
    return this.request<Conversation>(`/api/conversations/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  async deleteConversation(id: string): Promise<void> {
    await this.request<void>(`/api/conversations/${id}`, {
      method: "DELETE",
    });
  }

  // Messages
  async getMessages(conversationId: string): Promise<Message[]> {
    return this.request<Message[]>(
      `/api/conversations/${conversationId}/messages`
    );
  }

  // Health
  async checkHealth(): Promise<HealthResponse> {
    return this.request<HealthResponse>("/api/health");
  }
}

export const api = new ApiClient();
