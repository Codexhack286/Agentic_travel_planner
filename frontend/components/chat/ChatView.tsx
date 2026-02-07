"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useConversations } from "@/contexts/ConversationContext";
import { useChatStream } from "@/hooks/useChatStream";
import { MessageList } from "./MessageList";
import { ChatInput } from "./ChatInput";
import { SuggestedPrompts } from "./SuggestedPrompts";
import { AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ChatViewProps {
  conversationId: string | null;
}

export function ChatView({ conversationId }: ChatViewProps) {
  const router = useRouter();
  const [pendingMessage, setPendingMessage] = useState<string | null>(null);
  const { setActiveConversation, createConversation } = useConversations();
  const {
    messages,
    streamingContent,
    streamingToolResults,
    isStreaming,
    isLoading,
    error,
    sendMessage,
    stopStreaming,
    clearError,
  } = useChatStream(conversationId);

  // Sync active conversation in sidebar
  useEffect(() => {
    setActiveConversation(conversationId);
  }, [conversationId, setActiveConversation]);

  // Send pending message after conversation is created and navigation completes
  useEffect(() => {
    if (conversationId && pendingMessage) {
      sendMessage(pendingMessage);
      setPendingMessage(null);
    }
  }, [conversationId, pendingMessage, sendMessage]);

  const handleSend = async (content: string) => {
    // If no conversation exists, create one and navigate to it
    if (!conversationId) {
      try {
        setPendingMessage(content);
        const newConversation = await createConversation();
        router.push(`/chat/${newConversation.id}`);
        return;
      } catch (error) {
        console.error("Failed to create conversation:", error);
        setPendingMessage(null);
        return;
      }
    }

    await sendMessage(content);
  };

  const isEmpty = messages.length === 0 && !isStreaming && !isLoading;

  return (
    <div className="flex h-full flex-col">
      {/* Error banner */}
      {error && (
        <div className="flex items-center gap-2 border-b bg-destructive/10 px-4 py-2 text-sm text-destructive">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <p className="flex-1">{error}</p>
          <Button variant="ghost" size="sm" onClick={clearError}>
            Dismiss
          </Button>
        </div>
      )}

      {/* Empty state with suggested prompts */}
      {isEmpty ? (
        <div className="flex flex-1 items-center justify-center">
          <SuggestedPrompts onSelect={handleSend} />
        </div>
      ) : (
        <MessageList
          messages={messages}
          isStreaming={isStreaming}
          streamingContent={streamingContent}
          streamingToolResults={streamingToolResults}
        />
      )}

      {/* Chat input */}
      <ChatInput
        onSubmit={handleSend}
        onStop={stopStreaming}
        isStreaming={isStreaming}
        disabled={isLoading}
      />
    </div>
  );
}
