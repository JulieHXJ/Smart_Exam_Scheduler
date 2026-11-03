import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/features/auth/store";

function Splash() {
  return (
    <div className="grid min-h-svh place-items-center text-sm text-muted-foreground">
      Loading…
    </div>
  );
}

export function RequireAuth() {
  const status = useAuth((s) => s.status);
  if (status === "loading") return <Splash />;
  return status === "authenticated" ? (
    <Outlet />
  ) : (
    <Navigate to="/login" replace />
  );
}

export function GuestOnly() {
  const status = useAuth((s) => s.status);
  if (status === "loading") return <Splash />;
  return status === "authenticated" ? <Navigate to="/" replace /> : <Outlet />;
}
