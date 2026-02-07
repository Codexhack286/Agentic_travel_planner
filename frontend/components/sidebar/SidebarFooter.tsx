"use client";

import { Settings } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ThemeToggle } from "@/components/ThemeToggle";

export function SidebarFooter() {
  return (
    <div>
      <Separator />
      <div className="flex items-center justify-between p-4">
        <Button variant="ghost" size="sm" asChild>
          <Link href="/settings" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            Settings
          </Link>
        </Button>
        <ThemeToggle />
      </div>
    </div>
  );
}
