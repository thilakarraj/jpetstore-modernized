import { type ReactNode, useEffect } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const loadProfile = useAuthStore((s) => s.loadProfile);
  const isLoading = useAuthStore((s) => s.isLoading);
  const location = useLocation();

  useEffect(() => {
    void loadProfile();
  }, [loadProfile]);

  if (isLoading && !isAuthenticated) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center text-muted-foreground">
        Loading your account…
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/signon" replace state={{ from: location.pathname }} />;
  }

  return children;
}
