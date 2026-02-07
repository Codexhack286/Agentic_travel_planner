import { describe, it, expect, vi, beforeEach } from "vitest";
import { api } from "@/lib/api/client";
import { mockConversations } from "../../mocks/conversations";

const mockFetch = vi.fn();
global.fetch = mockFetch;

function jsonResponse(data: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
  };
}

describe("ApiClient", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it("getConversations returns a list of conversations", async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse(mockConversations));

    const result = await api.getConversations();

    expect(result).toEqual(mockConversations);
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/conversations"),
      expect.objectContaining({
        headers: expect.objectContaining({
          "Content-Type": "application/json",
        }),
      })
    );
  });

  it("createConversation sends POST with body", async () => {
    const newConv = { id: "conv-new", title: "New chat", createdAt: "", updatedAt: "" };
    mockFetch.mockResolvedValueOnce(jsonResponse(newConv));

    const result = await api.createConversation({ title: "New chat" });

    expect(result).toEqual(newConv);
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/conversations"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ title: "New chat" }),
      })
    );
  });

  it("throws ApiError on non-ok response", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      text: () => Promise.resolve("Not Found"),
    });

    await expect(api.getConversations()).rejects.toThrow("API Error 404");
  });
});
