"use client";

import { Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatTime } from "@/lib/format";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ToolResultCard } from "./tool-cards/ToolResultCard";
import { MarkdownRenderer } from "./MarkdownRenderer";
import type { Message } from "@/types";

interface MessageBubbleProps {
  message: Message;
  isStreaming?: boolean;
  streamingContent?: string;
}

export function MessageBubble({
  message,
  isStreaming,
  streamingContent,
}: MessageBubbleProps) {
  const isUser = message.role === "user";
  const content = isStreaming ? streamingContent || "" : message.content;

  return (
    <div
      className={cn(
        "flex gap-3 px-4 py-3",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
      role="article"
      aria-label={`${isUser ? "You" : "AI Assistant"} said`}
    >
      <Avatar className="h-8 w-8 shrink-0">
        <AvatarFallback
          className={cn(
            "text-xs",
            isUser
              ? "bg-primary text-primary-foreground"
              : "bg-accent text-accent-foreground"
          )}
        >
          {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
        </AvatarFallback>
      </Avatar>

      <div
        className={cn(
          "flex max-w-[80%] flex-col gap-2",
          isUser ? "items-end" : "items-start"
        )}
      >
        <div
          className={cn(
            "rounded-2xl px-4 py-2.5",
            isUser
              ? "bg-primary text-primary-foreground"
              : "bg-card border shadow-sm"
          )}
        >
          <div
            className={cn(
              "prose prose-sm max-w-none",
              isUser ? "prose-invert" : "dark:prose-invert",
              isStreaming && "streaming-cursor"
            )}
          >
            {isUser ? (
              content.split("\n").map((line, i) => (
                <p key={i} className={cn(i > 0 && "mt-2", !line && "h-4")}>
                  {line}
                </p>
              ))
            ) : (
              <MarkdownRenderer content={content} />
            )}
          </div>
        </div>

        {/* Tool result cards */}
        {message.toolResults && message.toolResults.length > 0 && (
          <div className="flex w-full flex-col gap-2">
            {message.toolResults.map((result, idx) => (
              <ToolResultCard key={idx} type={result.type} data={result.data} />
            ))}
          </div>
        )}

        <span className="text-xs text-muted-foreground">
          {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  );
}
