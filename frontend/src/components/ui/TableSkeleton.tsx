import styles from "./TableSkeleton.module.css";
import { Skeleton } from "./Skeleton";

type TableSkeletonProps = {
  columns?: number;
  rows?: number;
  className?: string;
};

export function TableSkeleton({ columns = 4, rows = 6, className }: TableSkeletonProps) {
  const columnArray = Array.from({ length: columns });
  const rowArray = Array.from({ length: rows });

  const containerClasses = [styles.container, className].filter(Boolean).join(" ");

  return (
    <div className={containerClasses} role="status" aria-live="polite" aria-busy="true">
      <div className={styles.header} style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}>
        {columnArray.map((_, index) => (
          <Skeleton key={`header-${index}`} height="1rem" className={styles.headerCell} />
        ))}
      </div>
      <div className={styles.body}>
        {rowArray.map((_, rowIndex) => (
          <div
            key={`row-${rowIndex}`}
            className={styles.row}
            style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}
          >
            {columnArray.map((__, columnIndex) => (
              <Skeleton key={`cell-${rowIndex}-${columnIndex}`} height="0.875rem" className={styles.cell} />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
