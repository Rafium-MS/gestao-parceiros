import { MouseEvent, ReactNode, useEffect, useId, useRef } from "react";
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
  const dialogRef = useRef<HTMLDivElement>(null);
  const titleId = useId();

  useEffect(() => {
    if (!isOpen || !dialogRef.current) {
      return;
    }

    const previouslyFocusedElement = document.activeElement as HTMLElement | null;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const getFocusableElements = () => {
      if (!dialogRef.current) {
        return [] as HTMLElement[];
      }

      return Array.from(
        dialogRef.current.querySelectorAll<HTMLElement>(
          'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), textarea:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])',
        ),
      ).filter(
        (element) =>
          !element.hasAttribute("data-focus-guard") &&
          element.tabIndex !== -1 &&
          (element.offsetWidth > 0 || element.offsetHeight > 0 || element.getClientRects().length > 0),
      );
    };

    const focusFirstElement = () => {
      const [firstFocusable] = getFocusableElements();
      if (firstFocusable) {
        firstFocusable.focus();
      } else {
        dialogRef.current?.focus();
      }
    };

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }

      if (event.key === "Tab") {
        const focusableElements = getFocusableElements();

        if (focusableElements.length === 0) {
          event.preventDefault();
          dialogRef.current?.focus();
          return;
        }

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        const activeElement = document.activeElement as HTMLElement | null;

        if (!event.shiftKey && activeElement === lastElement) {
          event.preventDefault();
          firstElement.focus();
        } else if (event.shiftKey && activeElement === firstElement) {
          event.preventDefault();
          lastElement.focus();
        }
      }

      if (event.key === "Enter") {
        const activeElement = document.activeElement as HTMLElement | null;
        if (activeElement === dialogRef.current) {
          const [firstFocusable] = getFocusableElements();
          firstFocusable?.click();
        }
      }
    };

    const keydownListener = (event: KeyboardEvent) => handleKeyDown(event);

    document.addEventListener("keydown", keydownListener);

    const focusTimer = window.setTimeout(focusFirstElement, 0);

    return () => {
      window.clearTimeout(focusTimer);
      document.removeEventListener("keydown", keydownListener);
      document.body.style.overflow = previousOverflow;
      previouslyFocusedElement?.focus();
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
    <div className={styles.backdrop} onMouseDown={handleBackdropClick}>
      <div
        ref={dialogRef}
        className={styles.dialog}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? titleId : undefined}
        tabIndex={-1}
      >
        {(title || onClose) && (
          <div className={styles.header}>
            {title ? (
              <h3 id={titleId} className={styles.title}>
                {title}
              </h3>
            ) : null}
            <button type="button" className={styles.closeButton} onClick={onClose} aria-label="Fechar">
              ×
            </button>
          </div>
        )}
        <div className={styles.content}>{children}</div>
        {footer ? <footer className={styles.footer}>{footer}</footer> : null}
      </div>
    </div>,
    document.body,
  );
}