import { Button } from "@/components/ui/button";
import { useAuth } from "@/features/auth/store";

export function HomePage() {
  const { user, signOut } = useAuth();
  return (
    <div className="grid min-h-svh place-items-center">
      <div className="space-y-4 text-center">
        <h1 className="text-2xl font-bold">Signed in</h1>
        <p className="text-muted-foreground">
          {user?.email} · {user?.role}
        </p>
        <Button variant="outline" onClick={signOut}>
          Sign out
        </Button>
      </div>
    </div>
  );
}
