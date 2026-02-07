"use client";

import { useState } from "react";
import { Menu } from "lucide-react";
import { ConversationProvider } from "@/contexts/ConversationContext";
import { AppSidebar } from "@/components/sidebar/AppSidebar";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { useIsMobile } from "@/hooks/useMediaQuery";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const isMobile = useIsMobile();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <ConversationProvider>
      <div className="flex h-dvh overflow-hidden">
        {/* Desktop sidebar */}
        {!isMobile && (
          <aside className="w-[280px] shrink-0 border-r">
            <AppSidebar />
          </aside>
        )}

        {/* Mobile sidebar (Sheet) */}
        {isMobile && (
          <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
            <SheetTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="fixed left-3 top-3 z-40 md:hidden"
              >
                <Menu className="h-5 w-5" />
                <span className="sr-only">Toggle sidebar</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-[280px] p-0">
              <SheetTitle className="sr-only">Navigation</SheetTitle>
              <AppSidebar
                onConversationSelect={() => setSidebarOpen(false)}
              />
            </SheetContent>
          </Sheet>
        )}

        {/* Main content */}
        <main className="flex-1 overflow-hidden">{children}</main>
      </div>
    </ConversationProvider>
  );
}
