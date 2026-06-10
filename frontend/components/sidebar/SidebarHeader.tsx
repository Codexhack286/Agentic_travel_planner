"use client";

import { Plus, Compass } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface SidebarHeaderProps {
  onNewChat: () => void;
}

export function SidebarHeader({ onNewChat }: SidebarHeaderProps) {
  return (
    <div className="flex items-center justify-between p-4">
      <div className="group flex items-center gap-2 select-none cursor-pointer">
        <Compass className="h-6 w-6 text-primary transition-transform duration-500 ease-out group-hover:rotate-90" />
        <span className="text-lg font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">Voyager AI</span>
      </div>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button variant="ghost" size="icon" onClick={onNewChat}>
            <Plus className="h-5 w-5" />
            <span className="sr-only">New chat</span>
          </Button>
        </TooltipTrigger>
        <TooltipContent>New chat</TooltipContent>
      </Tooltip>
    </div>
  );
}
