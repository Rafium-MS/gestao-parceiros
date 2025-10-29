import { ComponentType } from "react";
import { Navigate } from "react-router-dom";

import { useAuthGuard } from "@/hooks/useAuthGuard";

export function withAuthProtection<P>(Component: ComponentType<P>) {
  function WithAuthProtection(props: P) {
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

    return <Component {...props} />;
  }

  const componentName = Component.displayName ?? Component.name ?? "Component";
  WithAuthProtection.displayName = `withAuthProtection(${componentName})`;

  return WithAuthProtection;
}
