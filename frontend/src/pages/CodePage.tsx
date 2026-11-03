import { useEffect, useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSeparator,
  InputOTPSlot,
} from "@/components/ui/input-otp";
import { MailLinks } from "@/features/auth/components/MailLinks";
import { requestCode, verifyCode } from "@/features/auth/api";
import { useAuth } from "@/features/auth/store";
import { ApiError } from "@/lib/api";

// Backend alphabet: A-Z and 2-9 without I, O, 0, 1.
const CODE_PATTERN = "^[A-HJ-NP-Za-hj-np-z2-9]*$";
const RESEND_SECONDS = 30;

const slot = "h-14 w-11 text-xl font-semibold sm:w-12";

export function CodePage() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const email: string | undefined = state?.email;
  const [code, setCode] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cooldown, setCooldown] = useState(RESEND_SECONDS);

  useEffect(() => {
    if (cooldown <= 0) return;
    const t = setTimeout(() => setCooldown((c) => c - 1), 1000);
    return () => clearTimeout(t);
  }, [cooldown]);

  if (!email) return <Navigate to="/login" replace />;

  const submit = async (value: string) => {
    setBusy(true);
    setError(null);
    try {
      await verifyCode(email, value);
      await useAuth.getState().load();
      navigate("/", { replace: true });
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 429
          ? "Too many attempts. Please wait and try again."
          : "That code is invalid or has expired.",
      );
      setCode("");
    } finally {
      setBusy(false);
    }
  };

  const resend = async () => {
    setError(null);
    try {
      await requestCode(email);
      setCode("");
      setCooldown(RESEND_SECONDS);
    } catch {
      setError("We couldn't send a new code. Please try again later.");
    }
  };

  return (
    <div className="w-full max-w-[560px] text-center">
      <h1 className="text-4xl font-bold tracking-tight">
        We emailed you a code
      </h1>
      <p className="mx-auto mt-4 max-w-[460px] text-sm text-muted-foreground">
        We've sent an email to{" "}
        <strong className="text-foreground">{email}</strong>. Enter the code
        here to continue. It expires in 5 minutes. If you can't see the email,
        check your spam or junk folder.
      </p>

      <div className="mt-10 flex justify-center">
        <InputOTP
          maxLength={6}
          value={code}
          onChange={(v) => setCode(v.toUpperCase())}
          onComplete={submit}
          pattern={CODE_PATTERN}
          inputMode="text"
          autoCapitalize="characters"
          disabled={busy}
          autoFocus
        >
          <InputOTPGroup>
            <InputOTPSlot index={0} className={slot} />
            <InputOTPSlot index={1} className={slot} />
            <InputOTPSlot index={2} className={slot} />
          </InputOTPGroup>
          <InputOTPSeparator />
          <InputOTPGroup>
            <InputOTPSlot index={3} className={slot} />
            <InputOTPSlot index={4} className={slot} />
            <InputOTPSlot index={5} className={slot} />
          </InputOTPGroup>
        </InputOTP>
      </div>

      <p role="alert" className="mt-4 min-h-5 text-sm text-destructive">
        {error}
      </p>

      <div className="mt-4">
        <MailLinks email={email} />
      </div>

      <p className="mt-8 text-sm">
        Can't find your code?{" "}
        {cooldown > 0 ? (
          <span className="text-muted-foreground">
            Request a new one in {cooldown}s
          </span>
        ) : (
          <button
            type="button"
            onClick={resend}
            className="text-primary underline-offset-4 hover:underline"
          >
            Request a new code.
          </button>
        )}
      </p>
      <p className="mt-3 text-sm">
        <Link
          to="/login"
          className="text-muted-foreground underline-offset-4 hover:underline"
        >
          Use a different email
        </Link>
      </p>
    </div>
  );
}
