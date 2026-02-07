"use client";

import { useParams } from "next/navigation";
import { ChatView } from "@/components/chat/ChatView";

export default function ConversationPage() {
  const params = useParams<{ conversationId: string }>();

  return <ChatView conversationId={params.conversationId} />;
}
