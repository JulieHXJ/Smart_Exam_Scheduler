import { LoginForm } from "@/features/auth/components/LoginForm";

export function LoginPage() {
  return (
    <div className="w-full max-w-[560px] text-center">
      <h1 className="text-4xl font-bold tracking-tight">
        Enter your THA email address to sign in
      </h1>
      <p className="mt-3 text-sm text-muted-foreground">
        We'll email you a one-time code.
      </p>
      <div className="mx-auto mt-10 max-w-[440px] text-left">
        <LoginForm />
      </div>
    </div>
  );
}
