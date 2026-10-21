import { Outlet } from "react-router-dom"
import { Logo } from "@/components/logo"

export function AuthLayout() {
  return (
    <div className="flex min-h-svh flex-col bg-background text-foreground">
      <header className="px-8 py-6">
        <Logo />
      </header>
      <main className="flex flex-1 items-center justify-center px-4 pb-24">
        <Outlet />
      </main>
    </div>
  )
}