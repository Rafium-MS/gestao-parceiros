import { useLocation, type Location } from "react-router-dom";

import { useAuth } from "@/contexts/AuthContext";

export type AuthGuardResult = {
  isLoading: boolean;
  isAuthenticated: boolean;
  redirectTo?: string;
  redirectState?: { from: Location };
};

export function useAuthGuard(redirectPath = "/login"): AuthGuardResult {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return {
      isLoading: true,
      isAuthenticated: false,
    };
  }

  if (!isAuthenticated) {
    return {
      isLoading: false,
      isAuthenticated: false,
      redirectTo: redirectPath,
      redirectState: { from: location },
    };
  }

  return {
    isLoading: false,
    isAuthenticated: true,
  };
}
