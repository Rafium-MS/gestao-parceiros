import { ReactNode } from "react";

import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";

import styles from "./ConfirmDialog.module.css";

type DialogTone = "default" | "danger";

export type ConfirmDialogProps = {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  title?: ReactNode;
  description?: ReactNode;
  confirmLabel?: string;
  cancelLabel?: string;
  confirmVariant?: "primary" | "secondary" | "ghost" | "danger";
  tone?: DialogTone;
};

export function ConfirmDialog({
  isOpen,
  onConfirm,
  onCancel,
  title,
  description,
  confirmLabel = "Confirmar",
  cancelLabel = "Cancelar",
  confirmVariant = "primary",
  tone,
}: ConfirmDialogProps) {
  const dialogTone: DialogTone = tone ?? (confirmVariant === "danger" ? "danger" : "default");

  return (
    <Modal
      isOpen={isOpen}
      onClose={onCancel}
      title={null}
      footer={null}
    >
      <div className={`${styles.dialogContent} ${dialogTone === "danger" ? styles.toneDanger : ""}`}>
        {(title || dialogTone === "danger") && (
          <div className={styles.dialogHeader}>
            {dialogTone === "danger" ? <span className={styles.dialogIcon} aria-hidden>!</span> : null}
            <div>
              {title ? (
                <h3 className={styles.dialogTitle}>{title}</h3>
              ) : null}
              {description ? <p className={styles.dialogDescription}>{description}</p> : null}
            </div>
          </div>
        )}
        {!title && description && dialogTone !== "danger" ? (
          <p className={styles.dialogDescription}>{description}</p>
        ) : null}
        <div className={styles.dialogActions}>
          <Button variant="ghost" type="button" onClick={onCancel}>
            {cancelLabel}
          </Button>
          <Button variant={confirmVariant} type="button" onClick={onConfirm}>
            {confirmLabel}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
