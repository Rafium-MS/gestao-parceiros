import { HTMLAttributes, ReactNode } from "react";

import styles from "./Card.module.css";

type CardProps = {
  title?: ReactNode;
  subtitle?: ReactNode;
  actions?: ReactNode;
} & HTMLAttributes<HTMLDivElement>;

export function Card({ title, subtitle, actions, className, children, ...props }: CardProps) {
  return (
    <section className={[styles.card, className].filter(Boolean).join(" ")} {...props}>
      {(title || subtitle || actions) && (
        <header className={styles.header}>
          <div>
            {title ? <h2 className={styles.title}>{title}</h2> : null}
            {subtitle ? <p className={styles.subtitle}>{subtitle}</p> : null}
          </div>
          {actions ? <div>{actions}</div> : null}
        </header>
      )}
      {children}
    </section>
  );
}
