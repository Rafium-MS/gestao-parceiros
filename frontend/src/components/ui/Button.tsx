import { ButtonHTMLAttributes, ReactNode } from "react";

import styles from "./Button.module.css";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";
type ButtonSize = "sm" | "md" | "lg";

export type ButtonProps = {
  variant?: ButtonVariant;
  size?: ButtonSize;
  icon?: ReactNode;
  iconPosition?: "leading" | "trailing";
  isLoading?: boolean;
  loadingText?: string;
} & ButtonHTMLAttributes<HTMLButtonElement>;

export function Button({
  variant = "primary",
  size = "md",
  icon,
  iconPosition = "leading",
  className,
  children,
  isLoading = false,
  loadingText,
  disabled,
  ...props
}: ButtonProps) {
  const classes = [
    styles.button,
    styles[`variant${capitalize(variant)}` as keyof typeof styles],
    styles[`size${capitalize(size)}` as keyof typeof styles],
    !children && icon ? styles.iconOnly : undefined,
    className,
  ]
    .filter(Boolean)
    .join(" ");

  const showLeadingIcon = icon && iconPosition === "leading" && !isLoading;
  const showTrailingIcon = icon && iconPosition === "trailing" && !isLoading;
  const content = isLoading && loadingText ? loadingText : children;

  return (
    <button
      className={classes}
      data-loading={isLoading ? "true" : undefined}
      disabled={disabled || isLoading}
      aria-busy={isLoading}
      {...props}
    >
      {showLeadingIcon ? icon : null}
      {isLoading ? <span className={styles.spinner} aria-hidden="true" /> : null}
      {content}
      {showTrailingIcon ? icon : null}
    </button>
  );
}

function capitalize(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}
