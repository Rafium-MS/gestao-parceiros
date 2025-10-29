import { CSSProperties } from "react";

import styles from "./Skeleton.module.css";

type SkeletonProps = {
  className?: string;
  width?: number | string;
  height?: number | string;
  radius?: number | string;
};

export function Skeleton({ className, width, height, radius }: SkeletonProps) {
  const style: CSSProperties = {
    width,
    height,
    borderRadius: radius,
  };

  const classes = [styles.skeleton, className].filter(Boolean).join(" ");

  return <span className={classes} style={style} aria-hidden="true" />;
}
