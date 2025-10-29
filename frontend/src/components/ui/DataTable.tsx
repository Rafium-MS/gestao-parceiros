import { ReactNode } from "react";

import styles from "./DataTable.module.css";

export type TableColumn<T extends Record<string, unknown>> = {
  header: string;
  accessor?: keyof T;
  render?: (item: T) => ReactNode;
  align?: "left" | "right" | "center";
  width?: string;
};

export type DataTableProps<T extends Record<string, unknown>> = {
  columns: TableColumn<T>[];
  data: T[];
  emptyMessage?: string;
  keyExtractor?: (item: T, index: number) => string | number;
};

export function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  emptyMessage = "Nenhum dado disponível",
  keyExtractor,
}: DataTableProps<T>) {
  const columnCount = columns.length;

  return (
    <div className={styles.tableContainer}>
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.header} style={{ textAlign: column.align ?? "left", width: column.width }}>
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td className={styles.emptyState} colSpan={columnCount}>
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((item, index) => {
              const key = keyExtractor ? keyExtractor(item, index) : index;
              return (
                <tr key={key}>
                  {columns.map((column) => {
                    const content = column.render
                      ? column.render(item)
                      : column.accessor
                      ? (item[column.accessor] as ReactNode)
                      : null;

                    const alignClass =
                      column.align === "right"
                        ? styles.alignRight
                        : column.align === "center"
                        ? styles.alignCenter
                        : undefined;

                    return (
                      <td key={column.header} className={alignClass}>
                        {content}
                      </td>
                    );
                  })}
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
}
