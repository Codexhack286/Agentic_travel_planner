"use client";

import { useState, useRef, useEffect } from "react";
import { MessageSquare, MoreHorizontal, Pencil, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatRelativeDate } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { Conversation } from "@/types";

interface ConversationItemProps {
  conversation: Conversation;
  isActive: boolean;
  onSelect: () => void;
  onRename: (title: string) => void;
  onDelete: () => void;
}

export function ConversationItem({
  conversation,
  isActive,
  onSelect,
  onRename,
  onDelete,
}: ConversationItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(conversation.title);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditing) {
      inputRef.current?.focus();
      inputRef.current?.select();
    }
  }, [isEditing]);

  const handleSubmitRename = () => {
    const trimmed = editTitle.trim();
    if (trimmed && trimmed !== conversation.title) {
      onRename(trimmed);
    } else {
      setEditTitle(conversation.title);
    }
    setIsEditing(false);
  };

  return (
    <div
      className={cn(
        "group flex items-center gap-2 rounded-lg py-2.5 transition-all cursor-pointer relative duration-200",
        isActive
          ? "bg-primary/[0.08] text-primary border-l-2 border-l-primary rounded-l-none pl-2.5 font-semibold"
          : "text-muted-foreground hover:bg-muted/50 hover:text-foreground pl-3 border-l-2 border-l-transparent"
      )}
      onClick={!isEditing ? onSelect : undefined}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" && !isEditing) onSelect();
      }}
    >
      <MessageSquare className={cn("h-4 w-4 shrink-0 transition-transform duration-200 group-hover:scale-110", isActive ? "text-primary" : "text-muted-foreground/60")} />

      {isEditing ? (
        <Input
          ref={inputRef}
          value={editTitle}
          onChange={(e) => setEditTitle(e.target.value)}
          onBlur={handleSubmitRename}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleSubmitRename();
            if (e.key === "Escape") {
              setEditTitle(conversation.title);
              setIsEditing(false);
            }
          }}
          className="h-6 px-1 py-0 text-sm focus-visible:ring-1"
          onClick={(e) => e.stopPropagation()}
        />
      ) : (
        <div className="flex-1 truncate">
          <p className={cn("truncate text-sm font-medium", isActive ? "text-foreground font-semibold" : "text-foreground/90")}>
            {conversation.title || "New Chat"}
          </p>
          <p className="text-[11px] text-muted-foreground/85 mt-0.5">
            {formatRelativeDate(conversation.updatedAt)}
          </p>
        </div>
      )}

      {!isEditing && (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
              onClick={(e) => e.stopPropagation()}
            >
              <MoreHorizontal className="h-3.5 w-3.5" />
              <span className="sr-only">Actions</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation();
                setIsEditing(true);
              }}
            >
              <Pencil className="mr-2 h-3.5 w-3.5" />
              Rename
            </DropdownMenuItem>
            <DropdownMenuItem
              className="text-destructive focus:text-destructive"
              onClick={(e) => {
                e.stopPropagation();
                onDelete();
              }}
            >
              <Trash2 className="mr-2 h-3.5 w-3.5" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )}
    </div>
  );
}
