import { HTMLAttributes, ReactNode } from "react";

import styles from "./FormField.module.css";

type FormFieldProps = {
  label: ReactNode;
  htmlFor?: string;
  helperText?: ReactNode;
  error?: ReactNode;
  optional?: boolean;
} & HTMLAttributes<HTMLDivElement>;

export function FormField({
  label,
  htmlFor,
  helperText,
  error,
  optional,
  className,
  children,
  ...props
}: FormFieldProps) {
  return (
    <div className={[styles.field, className].filter(Boolean).join(" ")} {...props}>
      <div className={styles.labelRow}>
        <label className={styles.label} htmlFor={htmlFor}>
          {label}
        </label>
        {optional ? <span className={styles.optional}>Opcional</span> : null}
      </div>
      {children}
      {helperText ? <span className={styles.helper}>{helperText}</span> : null}
      {error ? <span className={styles.error}>{error}</span> : null}
    </div>
  );
}
