import type { CSSProperties } from "react";
import { Outlet } from "react-router-dom";
import { AppSidebar } from "@/components/layout/AppSidebar";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { TooltipProvider } from "@/components/ui/tooltip";

export function AppLayout() {
  return (
    <TooltipProvider delayDuration={200}>
      <SidebarProvider style={{ "--sidebar-width": "15rem" } as CSSProperties}>
        <AppSidebar />
        <SidebarInset className="bg-muted/40">
          {/* Temporary: branch 2 replaces this with the real top bar */}
          <header className="flex h-16 shrink-0 items-center border-b bg-background px-4">
            <SidebarTrigger />
          </header>
          <main className="mx-auto w-full max-w-[1600px] flex-1 p-8">
            <Outlet />
          </main>
        </SidebarInset>
      </SidebarProvider>
    </TooltipProvider>
  );
}
