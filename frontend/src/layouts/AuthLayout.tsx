import { Outlet } from "react-router-dom";
import { Logo } from "@/components/Logo";
import { ThemeToggleButton } from "@/components/layout/ThemeToggle";

export function AuthLayout() {
  return (
    <div className="flex min-h-svh flex-col bg-background text-foreground">
      <header className="flex items-center justify-between px-8 py-6">
        <Logo />
        <ThemeToggleButton />
      </header>
      <main className="flex flex-1 items-center justify-center px-4 pb-24">
        <Outlet />
      </main>
    </div>
  );
}
