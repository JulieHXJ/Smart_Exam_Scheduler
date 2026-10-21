import { LoginForm } from "@/features/auth/components/LoginForm"

export function LoginPage() {
  return (
    <div className="w-full max-w-[440px] rounded-2xl border bg-card p-9 shadow-sm">
      <h1 className="text-3xl font-bold tracking-tight">Welcome back</h1>
      <p className="mb-8 mt-2 text-sm text-muted-foreground">Log in to continue.</p>
      <LoginForm />
      <p className="mt-6 border-t pt-5 text-center text-xs text-muted-foreground">
        Use your university administration credentials.
      </p>
    </div>
  )
}