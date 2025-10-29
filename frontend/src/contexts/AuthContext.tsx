import {
  ReactNode,
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";

type AuthContextValue = {
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
};

const STORAGE_KEY = "gestao-parceiros.authenticated";

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function readInitialAuthState() {
  if (typeof window === "undefined") {
    return false;
  }

  try {
    return window.localStorage.getItem(STORAGE_KEY) === "true";
  } catch (error) {
    console.warn("Não foi possível ler o estado de autenticação persistido.", error);
    return false;
  }
}

type AuthProviderProps = {
  children: ReactNode;
};

export function AuthProvider({ children }: AuthProviderProps) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(readInitialAuthState);

  const login = useCallback(async (username: string, password: string) => {
    if (!username || !password) {
      throw new Error("Usuário e senha são obrigatórios.");
    }

    setIsAuthenticated(true);

    try {
      window.localStorage.setItem(STORAGE_KEY, "true");
    } catch (error) {
      console.warn("Não foi possível persistir o estado de autenticação.", error);
    }
  }, []);

  const logout = useCallback(() => {
    setIsAuthenticated(false);

    try {
      window.localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.warn("Não foi possível remover o estado de autenticação persistido.", error);
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      isAuthenticated,
      login,
      logout,
    }),
    [isAuthenticated, login, logout],
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
