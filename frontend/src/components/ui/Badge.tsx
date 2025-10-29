import { ReactNode } from "react";

import styles from "./Badge.module.css";

export type BadgeTone = "success" | "warning" | "danger" | "neutral";

export type BadgeProps = {
  tone?: BadgeTone;
  children: ReactNode;
  className?: string;
};

export function Badge({ tone = "neutral", children, className }: BadgeProps) {
  const classes = [styles.badge, styles[tone], className].filter(Boolean).join(" ");
  return <span className={classes}>{children}</span>;
}
