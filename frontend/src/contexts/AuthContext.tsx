import {
  ReactNode,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import { type AuthenticatedUser, fetchCurrentUser, login as apiLogin, logout as apiLogout } from "@/services/auth";
import { HttpError, onUnauthorized } from "@/services/httpClient";

type AuthContextValue = {
  user: AuthenticatedUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<AuthenticatedUser>;
  logout: () => Promise<void>;
  renewSession: () => Promise<AuthenticatedUser | null>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

type AuthProviderProps = {
  children: ReactNode;
};

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const isMountedRef = useRef(true);

  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    if (!username || !password) {
      throw new Error("Usuário e senha são obrigatórios.");
    }

    try {
      const authenticated = await apiLogin(username, password);
      if (isMountedRef.current) {
        setUser(authenticated);
      }
      return authenticated;
    } catch (error) {
      if (error instanceof HttpError) {
        throw new Error(error.message);
      }
      throw error;
    }
  }, []);

  const renewSession = useCallback(async () => {
    try {
      const currentUser = await fetchCurrentUser();
      if (isMountedRef.current) {
        setUser(currentUser);
      }
      return currentUser;
    } catch (error) {
      if (error instanceof HttpError && error.status === 401) {
        if (isMountedRef.current) {
          setUser(null);
        }
        return null;
      }
      throw error;
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiLogout();
    } finally {
      if (isMountedRef.current) {
        setUser(null);
      }
    }
  }, []);

  useEffect(() => {
    const detachUnauthorized = onUnauthorized(() => {
      if (isMountedRef.current) {
        setUser(null);
      }
    });

    renewSession()
      .catch(() => {
        if (isMountedRef.current) {
          setUser(null);
        }
      })
      .finally(() => {
        if (isMountedRef.current) {
          setIsLoading(false);
        }
      });

    return () => {
      detachUnauthorized();
    };
  }, [renewSession]);

  useEffect(() => {
    if (!user) {
      return undefined;
    }

    const RENEW_INTERVAL = 5 * 60 * 1000;

    const renew = () => {
      renewSession().catch((error) => {
        if (!(error instanceof HttpError)) {
          console.error("Falha ao renovar sessão", error);
        }
      });
    };

    const intervalId = window.setInterval(renew, RENEW_INTERVAL);
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        renew();
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      window.clearInterval(intervalId);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [renewSession, user]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isLoading,
      login,
      logout,
      renewSession,
    }),
    [isLoading, login, logout, renewSession, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth deve ser utilizado dentro de um AuthProvider.");
  }

  return context;
}
