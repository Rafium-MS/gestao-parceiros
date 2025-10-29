import { forwardRef, SelectHTMLAttributes } from "react";

import styles from "./Input.module.css";

type SelectInputProps = SelectHTMLAttributes<HTMLSelectElement> & {
  hasError?: boolean;
};

export const SelectInput = forwardRef<HTMLSelectElement, SelectInputProps>(function SelectInput(
  { className, hasError, children, ...props },
  ref,
) {
  return (
    <select
      ref={ref}
      className={[styles.select, hasError ? styles.error : undefined, className].filter(Boolean).join(" ")}
      {...props}
    >
      {children}
    </select>
  );
});
