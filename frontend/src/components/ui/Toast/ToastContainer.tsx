import styles from "./ToastContainer.module.css";

export type ToastDefinition = {
  id: string;
  type: "success" | "error" | "warning";
  message: string;
};

type ToastContainerProps = {
  toasts: ToastDefinition[];
  onDismiss: (id: string) => void;
};

const ICONS: Record<ToastDefinition["type"], string> = {
  success: "✓",
  error: "✗",
  warning: "!",
};

const ARIA_ROLES: Record<ToastDefinition["type"], "status" | "alert"> = {
  success: "status",
  warning: "status",
  error: "alert",
};

export function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  if (toasts.length === 0) {
    return null;
  }

  return (
    <div className={styles.toastContainer} role="region" aria-live="polite" aria-label="Notificações">
      {toasts.map((toast) => {
        const typeClass = styles[`toast${capitalize(toast.type)}`];
        const toastClassName = typeClass ? `${styles.toast} ${typeClass}` : styles.toast;
        return (
          <div key={toast.id} className={toastClassName} role={ARIA_ROLES[toast.type]}>
            <span className={styles.icon} aria-hidden="true">
              {ICONS[toast.type]}
            </span>
            <span className={styles.message}>{toast.message}</span>
            <button type="button" className={styles.dismissButton} onClick={() => onDismiss(toast.id)} aria-label="Fechar">
              ×
            </button>
          </div>
        );
      })}
    </div>
  );
}

function capitalize(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}
