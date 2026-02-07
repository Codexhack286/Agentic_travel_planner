"use client";

import { MessageBubble } from "./MessageBubble";
import { StreamingIndicator } from "./StreamingIndicator";
import { useAutoScroll } from "@/hooks/useAutoScroll";
import type { Message, ToolResult } from "@/types";

interface MessageListProps {
  messages: Message[];
  isStreaming: boolean;
  streamingContent: string;
  streamingToolResults: ToolResult[];
}

export function MessageList({
  messages,
  isStreaming,
  streamingContent,
  streamingToolResults,
}: MessageListProps) {
  const { scrollRef, handleScroll } = useAutoScroll(
    streamingContent || messages.length
  );

  return (
    <div
      ref={scrollRef}
      onScroll={handleScroll}
      className="flex-1 overflow-y-auto custom-scrollbar"
      role="log"
      aria-label="Chat messages"
      aria-live="polite"
    >
      <div className="mx-auto max-w-3xl py-4">
        {messages.map((msg, idx) => (
          <MessageBubble key={msg.id || idx} message={msg} />
        ))}

        {/* Streaming message in progress */}
        {isStreaming && streamingContent && (
          <MessageBubble
            message={{
              role: "assistant",
              content: streamingContent,
              toolResults: streamingToolResults,
              timestamp: new Date().toISOString(),
            }}
            isStreaming
            streamingContent={streamingContent}
          />
        )}

        {/* Streaming indicator (before first token) */}
        {isStreaming && !streamingContent && (
          <div className="flex gap-3 px-4 py-3">
            <div className="h-8 w-8" /> {/* Avatar spacer */}
            <StreamingIndicator />
          </div>
        )}
      </div>
    </div>
  );
}
