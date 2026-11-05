import { useEffect, useRef, useState } from "react";
import { Bell, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { ThemeToggle } from "./ThemeToggle";

// Placeholder terms until real planning cycles are connected
const TERMS = [
  { value: "ws2026", label: "Winter semester 2026/27" },
  { value: "ss2026", label: "Summer semester 2026" },
];

export function TopBar() {
  const [term, setTerm] = useState(TERMS[0].value);
  const searchRef = useRef<HTMLInputElement>(null);

  // Ctrl/Cmd + K focuses the search field
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        searchRef.current?.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <header className="sticky top-0 z-10 flex h-16 shrink-0 items-center gap-4 border-b bg-background px-6">
      <SidebarTrigger />

      <div className="flex items-center gap-3">
        <span className="size-2 rounded-full bg-primary" aria-hidden />
        <div className="leading-tight">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
            Active term
          </p>
          <select
            value={term}
            onChange={(event) => setTerm(event.target.value)}
            aria-label="Active term"
            className="h-7 cursor-pointer appearance-none rounded-md border-0 bg-transparent p-0 pr-2 text-sm font-semibold shadow-none outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            {TERMS.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="ml-auto flex items-center gap-3">
        <div className="relative hidden w-80 md:block">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            ref={searchRef}
            type="search"
            placeholder="Search exams, rooms, examiners…"
            className="h-10 pl-9 pr-14"
          />
          <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 rounded border bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
            ⌘ K
          </span>
        </div>

        <Button
          variant="outline"
          size="icon"
          className="relative size-10"
          aria-label="Notifications"
        >
          <Bell className="size-4" />
          <span
            className="absolute right-2.5 top-2.5 size-2 rounded-full bg-primary"
            aria-hidden
          />
        </Button>

        <ThemeToggle />

      </div>
    </header>
  );
}
