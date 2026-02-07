"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import type { Message, ToolResult } from "@/types";
import { streamChat } from "@/lib/api/chat";
import { api } from "@/lib/api/client";

export interface UseChatStreamReturn {
  messages: Message[];
  streamingContent: string;
  streamingToolResults: ToolResult[];
  isStreaming: boolean;
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  stopStreaming: () => void;
  clearError: () => void;
}

export function useChatStream(
  conversationId: string | null
): UseChatStreamReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [streamingContent, setStreamingContent] = useState("");
  const [streamingToolResults, setStreamingToolResults] = useState<
    ToolResult[]
  >([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Load existing messages when conversationId changes
  useEffect(() => {
    if (!conversationId) {
      setMessages([]);
      return;
    }

    let cancelled = false;
    setIsLoading(true);

    api
      .getMessages(conversationId)
      .then((msgs) => {
        if (!cancelled) setMessages(msgs);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [conversationId]);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!conversationId || !content.trim()) return;

      // Add user message optimistically
      const userMessage: Message = {
        role: "user",
        content: content.trim(),
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setStreamingContent("");
      setStreamingToolResults([]);
      setIsStreaming(true);
      setError(null);

      // Create abort controller
      abortControllerRef.current = new AbortController();

      try {
        let fullContent = "";
        const allToolResults: ToolResult[] = [];

        await streamChat(
          conversationId,
          content.trim(),
          {
            onToken: (token) => {
              fullContent += token;
              setStreamingContent(fullContent);
            },
            onToolResult: (toolResult) => {
              allToolResults.push(toolResult);
              setStreamingToolResults([...allToolResults]);
            },
            onComplete: (completedContent, toolResults) => {
              const assistantMessage: Message = {
                role: "assistant",
                content: completedContent,
                toolResults,
                timestamp: new Date().toISOString(),
              };
              setMessages((prev) => [...prev, assistantMessage]);
              setStreamingContent("");
              setStreamingToolResults([]);
              setIsStreaming(false);
            },
            onError: (err) => {
              setError(err.message);
              setIsStreaming(false);
            },
          },
          abortControllerRef.current.signal
        );
      } catch (err) {
        if ((err as Error).name === "AbortError") {
          // User aborted — commit partial content
          if (streamingContent) {
            const partialMessage: Message = {
              role: "assistant",
              content:
                streamingContent + "\n\n*[Response stopped by user]*",
              timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, partialMessage]);
          }
        } else {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to send message. Please try again."
          );
        }
        setStreamingContent("");
        setStreamingToolResults([]);
        setIsStreaming(false);
      }
    },
    [conversationId, streamingContent]
  );

  const stopStreaming = useCallback(() => {
    abortControllerRef.current?.abort();
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    messages,
    streamingContent,
    streamingToolResults,
    isStreaming,
    isLoading,
    error,
    sendMessage,
    stopStreaming,
    clearError,
  };
}
