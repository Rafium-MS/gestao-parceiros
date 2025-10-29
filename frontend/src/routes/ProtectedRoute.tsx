import { Navigate, Outlet } from "react-router-dom";

import { useAuthGuard } from "@/hooks/useAuthGuard";

export function ProtectedRoute() {
  const { isAuthenticated, isLoading, redirectState, redirectTo } = useAuthGuard();

  if (isLoading) {
    return (
      <div className="page-loading" role="status">
        Carregando...
      </div>
    );
  }

  if (!isAuthenticated && redirectTo) {
    return <Navigate to={redirectTo} replace state={redirectState} />;
  }

  return <Outlet />;
}
