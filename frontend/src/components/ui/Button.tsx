import { ButtonHTMLAttributes, ReactNode } from "react";

import styles from "./Button.module.css";

type ButtonVariant = "primary" | "secondary" | "ghost";
type ButtonSize = "sm" | "md" | "lg";

export type ButtonProps = {
  variant?: ButtonVariant;
  size?: ButtonSize;
  icon?: ReactNode;
  iconPosition?: "leading" | "trailing";
} & ButtonHTMLAttributes<HTMLButtonElement>;

export function Button({
  variant = "primary",
  size = "md",
  icon,
  iconPosition = "leading",
  className,
  children,
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

  return (
    <button className={classes} {...props}>
      {icon && iconPosition === "leading" ? icon : null}
      {children}
      {icon && iconPosition === "trailing" ? icon : null}
    </button>
  );
}

function capitalize(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}
