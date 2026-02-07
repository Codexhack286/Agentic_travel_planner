"use client";

import { useRouter } from "next/navigation";
import { useConversations } from "@/contexts/ConversationContext";
import { SidebarHeader } from "./SidebarHeader";
import { ConversationList } from "./ConversationList";
import { SidebarFooter } from "./SidebarFooter";
import { Separator } from "@/components/ui/separator";

interface AppSidebarProps {
  onConversationSelect?: () => void;
}

export function AppSidebar({ onConversationSelect }: AppSidebarProps) {
  const router = useRouter();
  const {
    conversations,
    activeId,
    isLoading,
    createConversation,
    renameConversation,
    deleteConversation,
    setActiveConversation,
  } = useConversations();

  const handleNewChat = async () => {
    try {
      const conv = await createConversation();
      router.push(`/chat/${conv.id}`);
      onConversationSelect?.();
    } catch {
      // Fall back to new chat page
      router.push("/chat");
      onConversationSelect?.();
    }
  };

  const handleSelect = (id: string) => {
    setActiveConversation(id);
    router.push(`/chat/${id}`);
    onConversationSelect?.();
  };

  const handleDelete = async (id: string) => {
    await deleteConversation(id);
    if (activeId === id) {
      router.push("/chat");
    }
  };

  return (
    <div className="flex h-full flex-col bg-card">
      <SidebarHeader onNewChat={handleNewChat} />
      <Separator />
      <ConversationList
        conversations={conversations}
        activeId={activeId}
        isLoading={isLoading}
        onSelect={handleSelect}
        onRename={renameConversation}
        onDelete={handleDelete}
      />
      <SidebarFooter />
    </div>
  );
}
