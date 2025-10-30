import { Link, useLocation } from "react-router-dom";
import { useMemo } from "react";

import { breadcrumbMap } from "@/routes/config";

import styles from "./Breadcrumbs.module.css";

const ROOT_PATH = "/";
const ROOT_LABEL = breadcrumbMap[ROOT_PATH] ?? "Início";

const formatSegment = (segment: string) => {
  if (segment === "") {
    return ROOT_LABEL;
  }

  return segment
    .split("-")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ")
    .trim();
};

type Crumb = {
  path: string;
  label: string;
  isCurrent: boolean;
};

export function Breadcrumbs() {
  const location = useLocation();

  const crumbs = useMemo<Crumb[]>(() => {
    const segments = location.pathname.split("/").filter(Boolean);

    const items: Crumb[] = [
      {
        path: ROOT_PATH,
        label: ROOT_LABEL,
        isCurrent: segments.length === 0,
      },
    ];

    segments.forEach((segment, index) => {
      const path = `/${segments.slice(0, index + 1).join("/")}`;
      const label = breadcrumbMap[path] ?? formatSegment(segment);

      items.push({
        path,
        label,
        isCurrent: index === segments.length - 1,
      });
    });

    return items;
  }, [location.pathname]);

  if (crumbs.length <= 1) {
    return (
      <nav aria-label="Trilha de navegação" className={styles.wrapper}>
        <ol className={styles.list}>
          <li className={styles.item}>
            <span className={styles.current} aria-current="page">{ROOT_LABEL}</span>
          </li>
        </ol>
      </nav>
    );
  }

  return (
    <nav aria-label="Trilha de navegação" className={styles.wrapper}>
      <ol className={styles.list}>
        {crumbs.map((crumb, index) => (
          <li key={crumb.path} className={styles.item}>
            {crumb.isCurrent ? (
              <span className={styles.current} aria-current="page">
                {crumb.label}
              </span>
            ) : (
              <Link className={styles.link} to={crumb.path}>
                {crumb.label}
              </Link>
            )}
            {index < crumbs.length - 1 ? <span className={styles.separator}>/</span> : null}
          </li>
        ))}
      </ol>
    </nav>
  );
}
