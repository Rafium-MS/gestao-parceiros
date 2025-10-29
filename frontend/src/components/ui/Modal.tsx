import { MouseEvent, ReactNode, useEffect } from "react";
import { createPortal } from "react-dom";

import styles from "./Modal.module.css";

type ModalProps = {
  isOpen: boolean;
  onClose: () => void;
  title?: ReactNode;
  footer?: ReactNode;
  children: ReactNode;
};

export function Modal({ isOpen, onClose, title, footer, children }: ModalProps) {
  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    document.addEventListener("keydown", handleKeyDown);

    const { overflow } = document.body.style;
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = overflow;
    };
  }, [isOpen, onClose]);

  if (!isOpen) {
    return null;
  }

  const handleBackdropClick = (event: MouseEvent<HTMLDivElement>) => {
    if (event.target === event.currentTarget) {
      onClose();
    }
  };

  return createPortal(
    <div
      className={styles.backdrop}
      role="dialog"
      aria-modal
      aria-label={typeof title === "string" ? title : undefined}
      onMouseDown={handleBackdropClick}
    >
      <div className={styles.dialog}>
        {(title || onClose) && (
          <div className={styles.header}>
            {title ? <h3 className={styles.title}>{title}</h3> : null}
            <button type="button" className={styles.closeButton} onClick={onClose} aria-label="Fechar">
              ×
            </button>
          </div>
        )}
        <div>{children}</div>
        {footer ? <footer className={styles.footer}>{footer}</footer> : null}
      </div>
    </div>,
    document.body,
  );
}
