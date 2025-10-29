import { forwardRef, InputHTMLAttributes } from "react";

import styles from "./Input.module.css";

type TextInputProps = InputHTMLAttributes<HTMLInputElement> & {
  hasError?: boolean;
};

export const TextInput = forwardRef<HTMLInputElement, TextInputProps>(function TextInput(
  { className, hasError, ...props },
  ref,
) {
  return (
    <input
      ref={ref}
      className={[styles.input, hasError ? styles.error : undefined, className].filter(Boolean).join(" ")}
      {...props}
    />
  );
});
