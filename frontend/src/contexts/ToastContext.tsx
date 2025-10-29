import { createContext, ReactNode, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";

import { ToastContainer, type ToastDefinition } from "@/components/ui/Toast/ToastContainer";

type ToastType = "success" | "error" | "warning";

type ToastOptions = {
  duration?: number;
};

type AddToastInput = {
  type: ToastType;
  message: string;
  duration?: number;
};

type ToastContextValue = {
  addToast: (toast: AddToastInput) => string;
  removeToast: (id: string) => void;
  showSuccess: (message: string, options?: ToastOptions) => string;
  showError: (message: string, options?: ToastOptions) => string;
  showWarning: (message: string, options?: ToastOptions) => string;
};

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

const DEFAULT_DURATION = 4000;

type ToastProviderProps = {
  children: ReactNode;
};

export function ToastProvider({ children }: ToastProviderProps) {
  const [toasts, setToasts] = useState<ToastDefinition[]>([]);
  const timers = useRef<Record<string, number>>({});

  const removeToast = useCallback((id: string) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
    const timeoutId = timers.current[id];
    if (timeoutId) {
      window.clearTimeout(timeoutId);
      delete timers.current[id];
    }
  }, []);

  const addToast = useCallback(
    ({ type, message, duration }: AddToastInput) => {
      const id = typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID() : Math.random().toString(36).slice(2);
      const timeout = duration ?? DEFAULT_DURATION;
      setToasts((current) => [...current, { id, type, message }]);
      if (timeout > 0) {
        const timeoutId = window.setTimeout(() => {
          removeToast(id);
        }, timeout);
        timers.current[id] = timeoutId;
      }
      return id;
    },
    [removeToast],
  );

  useEffect(() => {
    return () => {
      Object.values(timers.current).forEach((timeoutId) => {
        window.clearTimeout(timeoutId);
      });
      timers.current = {};
    };
  }, []);

  const contextValue = useMemo<ToastContextValue>(() => {
    const showSuccess = (message: string, options?: ToastOptions) => addToast({ type: "success", message, ...options });
    const showError = (message: string, options?: ToastOptions) => addToast({ type: "error", message, ...options });
    const showWarning = (message: string, options?: ToastOptions) => addToast({ type: "warning", message, ...options });

    return {
      addToast,
      removeToast,
      showSuccess,
      showError,
      showWarning,
    };
  }, [addToast, removeToast]);

  return (
    <ToastContext.Provider value={contextValue}>
      {children}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast deve ser usado dentro de um ToastProvider");
  }
  return context;
}
