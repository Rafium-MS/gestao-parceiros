import { ReactNode, createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { type AuthenticatedUser, fetchCurrentUser, login as apiLogin, logout as apiLogout } from "@/services/auth";
import { HttpError, onUnauthorized } from "@/services/httpClient";

type AuthContextValue = {
  user: AuthenticatedUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

type AuthProviderProps = {
  children: ReactNode;
};

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const detachUnauthorized = onUnauthorized(() => {
      if (isMounted) {
        setUser(null);
      }
    });

    fetchCurrentUser()
      .then((currentUser) => {
        if (isMounted) {
          setUser(currentUser);
        }
      })
      .catch(() => {
        if (isMounted) {
          setUser(null);
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
      detachUnauthorized();
    };
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    if (!username || !password) {
      throw new Error("Usuário e senha são obrigatórios.");
    }

    try {
      const authenticated = await apiLogin(username, password);
      setUser(authenticated);
    } catch (error) {
      if (error instanceof HttpError) {
        throw new Error(error.message);
      }
      throw error;
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiLogout();
    } finally {
      setUser(null);
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isLoading,
      login,
      logout,
    }),
    [isLoading, login, logout, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth deve ser utilizado dentro de um AuthProvider.");
  }

  return context;
}
