import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { IconInput } from "./IconInput";
import { requestCode } from "../api";
import { ApiError } from "@/lib/api";

export function LoginForm() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const normalized = email.trim().toLowerCase();
    setBusy(true);
    setError(null);
    try {
      await requestCode(normalized);
      navigate("/login/code", { state: { email: normalized } });
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 429
          ? "Too many requests. Please try again later."
          : "We couldn't send the email. Please try again.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <IconInput
        id="email"
        label="Email address"
        icon={Mail}
        type="email"
        placeholder="name@tha.de"
        autoComplete="email"
        autoFocus
        required
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      {error && (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}
      <Button
        type="submit"
        disabled={busy}
        className="h-11 w-full gap-2 whitespace-nowrap"
      >
        {busy ? "Sending code…" : "Sign in with email"}
        {!busy && <ArrowRight className="size-4" />}
      </Button>
    </form>
  );
}
