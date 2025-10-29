import { ReactNode, useEffect, useMemo, useState } from "react";

import styles from "./DataTable.module.css";

export type TableColumn<T extends Record<string, unknown>> = {
  header: string;
  accessor?: keyof T;
  render?: (item: T) => ReactNode;
  align?: "left" | "right" | "center";
  width?: string;
  sortable?: boolean;
  sortAccessor?: keyof T;
  sortValue?: (item: T) => string | number | Date | boolean | null | undefined;
  exportValue?: (item: T) => string | number | boolean | null | undefined;
  disableExport?: boolean;
};

export type DataTableProps<T extends Record<string, unknown>> = {
  columns: TableColumn<T>[];
  data: T[];
  emptyMessage?: string;
  keyExtractor?: (item: T, index: number) => string | number;
  enableSorting?: boolean;
  initialSort?: { columnKey: string; direction: SortDirection };
  enablePagination?: boolean;
  initialPageSize?: number;
  pageSizeOptions?: number[];
  enableSelection?: boolean;
  onSelectionChange?: (selectedItems: T[]) => void;
  selectionActions?: (selectedItems: T[], clearSelection: () => void) => ReactNode;
  enableExport?: boolean;
  exportFileName?: string;
};

type SortDirection = "asc" | "desc";

type SortState<T> = {
  columnKey: string;
  direction: SortDirection;
  comparator: (a: T, b: T) => number;
};

type KeyedItem<T> = { key: string | number; item: T };

function getColumnKey<T extends Record<string, unknown>>(column: TableColumn<T>) {
  return column.accessor ? String(column.accessor) : column.header;
}

function getSortValue<T extends Record<string, unknown>>(column: TableColumn<T>, item: T) {
  if (column.sortValue) {
    return column.sortValue(item);
  }
  if (column.sortAccessor) {
    return item[column.sortAccessor];
  }
  if (column.accessor) {
    return item[column.accessor];
  }
  return null;
}

function compareValues(valueA: unknown, valueB: unknown) {
  if (valueA === valueB) {
    return 0;
  }
  if (valueA === null || valueA === undefined) {
    return -1;
  }
  if (valueB === null || valueB === undefined) {
    return 1;
  }
  if (valueA instanceof Date && valueB instanceof Date) {
    return valueA.getTime() - valueB.getTime();
  }
  if (typeof valueA === "number" && typeof valueB === "number") {
    return valueA - valueB;
  }
  const normalizedA = String(valueA).toLowerCase();
  const normalizedB = String(valueB).toLowerCase();
  if (normalizedA < normalizedB) {
    return -1;
  }
  if (normalizedA > normalizedB) {
    return 1;
  }
  return 0;
}

function resolveExportValue(value: unknown) {
  if (value === null || value === undefined) {
    return "";
  }
  if (value instanceof Date) {
    return value.toISOString();
  }
  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }
  return String(value);
}

function downloadFile(content: string, mimeType: string, fileName: string) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();
  URL.revokeObjectURL(url);
}

function exportToCsv<T extends Record<string, unknown>>(columns: TableColumn<T>[], data: T[], fileName: string) {
  const activeColumns = columns.filter((column) => !column.disableExport);
  const header = activeColumns.map((column) => `"${column.header.replaceAll('"', '""')}"`).join(",");
  const rows = data.map((row) =>
    activeColumns
      .map((column) => {
        const rawValue = column.exportValue
          ? column.exportValue(row)
          : column.accessor
          ? row[column.accessor]
          : null;
        const value = resolveExportValue(rawValue);
        const escaped = value.replaceAll('"', '""');
        return `"${escaped}"`;
      })
      .join(","),
  );

  downloadFile([header, ...rows].join("\n"), "text/csv;charset=utf-8;", `${fileName}.csv`);
}

function exportToExcel<T extends Record<string, unknown>>(columns: TableColumn<T>[], data: T[], fileName: string) {
  const activeColumns = columns.filter((column) => !column.disableExport);
  const header = activeColumns.map((column) => `<th>${column.header}</th>`).join("");
  const rows = data
    .map((row) => {
      const cells = activeColumns
        .map((column) => {
          const rawValue = column.exportValue
            ? column.exportValue(row)
            : column.accessor
            ? row[column.accessor]
            : null;
          return `<td>${resolveExportValue(rawValue)}</td>`;
        })
        .join("");
      return `<tr>${cells}</tr>`;
    })
    .join("");

  const tableHtml = `<table><thead><tr>${header}</tr></thead><tbody>${rows}</tbody></table>`;
  const excelContent = `<!DOCTYPE html><html><head><meta charset="utf-8" /></head><body>${tableHtml}</body></html>`;
  downloadFile(excelContent, "application/vnd.ms-excel", `${fileName}.xls`);
}

export function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  emptyMessage = "Nenhum dado disponível",
  keyExtractor,
  enableSorting = false,
  initialSort,
  enablePagination = false,
  initialPageSize = 10,
  pageSizeOptions = [10, 25, 50],
  enableSelection = false,
  onSelectionChange,
  selectionActions,
  enableExport = false,
  exportFileName = "dados",
}: DataTableProps<T>) {
  const [sortState, setSortState] = useState<SortState<T> | null>(() => {
    if (!enableSorting || !initialSort) {
      return null;
    }
    const column = columns.find((item) => getColumnKey(item) === initialSort.columnKey);
    if (!column || !column.sortable) {
      return null;
    }
    const direction = initialSort.direction;
    return {
      columnKey: getColumnKey(column),
      direction,
      comparator: (a: T, b: T) => {
        const valueA = getSortValue(column, a);
        const valueB = getSortValue(column, b);
        return compareValues(valueA, valueB);
      },
    };
  });

  const [pageSize, setPageSize] = useState(initialPageSize);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedKeys, setSelectedKeys] = useState<Set<string | number>>(new Set());

  const keyedData = useMemo<KeyedItem<T>[]>(() => {
    return data.map((item, index) => ({
      item,
      key: keyExtractor ? keyExtractor(item, index) : index,
    }));
  }, [data, keyExtractor]);

  const sortedItems = useMemo(() => {
    if (!enableSorting || !sortState) {
      return keyedData;
    }
    const sorted = [...keyedData].sort((a, b) => {
      const result = sortState.comparator(a.item, b.item);
      return sortState.direction === "asc" ? result : -result;
    });
    return sorted;
  }, [enableSorting, keyedData, sortState]);

  const totalItems = sortedItems.length;
  const totalPages = enablePagination ? Math.max(1, Math.ceil(totalItems / pageSize)) : 1;

  useEffect(() => {
    if (!enablePagination) {
      return;
    }
    setCurrentPage((previous) => (previous > totalPages ? totalPages : previous));
  }, [enablePagination, totalPages]);

  useEffect(() => {
    setSelectedKeys((previous) => {
      if (previous.size === 0) {
        return previous;
      }
      const availableKeys = new Set(sortedItems.map((row) => row.key));
      const next = new Set(Array.from(previous).filter((key) => availableKeys.has(key)));
      if (next.size === previous.size) {
        return previous;
      }
      return next;
    });
  }, [sortedItems]);

  const paginatedItems = useMemo(() => {
    if (!enablePagination) {
      return sortedItems;
    }
    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    return sortedItems.slice(start, end);
  }, [enablePagination, sortedItems, currentPage, pageSize]);

  const selectedItems = useMemo(() => {
    if (!enableSelection || selectedKeys.size === 0) {
      return [];
    }
    return sortedItems
      .filter((row) => selectedKeys.has(row.key))
      .map((row) => row.item);
  }, [enableSelection, selectedKeys, sortedItems]);

  useEffect(() => {
    if (onSelectionChange) {
      onSelectionChange(selectedItems);
    }
  }, [selectedItems, onSelectionChange]);

  const handleSort = (column: TableColumn<T>) => {
    if (!enableSorting || !column.sortable) {
      return;
    }
    const columnKey = getColumnKey(column);
    setSortState((previous) => {
      if (!previous || previous.columnKey !== columnKey) {
        return {
          columnKey,
          direction: "asc",
          comparator: (a: T, b: T) => compareValues(getSortValue(column, a), getSortValue(column, b)),
        };
      }
      const nextDirection = previous.direction === "asc" ? "desc" : "asc";
      return { ...previous, direction: nextDirection };
    });
  };

  const isColumnSorted = (column: TableColumn<T>) => sortState?.columnKey === getColumnKey(column);

  const toggleRowSelection = (key: string | number) => {
    if (!enableSelection) {
      return;
    }
    setSelectedKeys((previous) => {
      const next = new Set(previous);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  const clearSelection = () => {
    setSelectedKeys(new Set());
  };

  const allVisibleSelected = enableSelection
    ? paginatedItems.length > 0 && paginatedItems.every((row) => selectedKeys.has(row.key))
    : false;

  const handleToggleAllVisible = () => {
    if (!enableSelection) {
      return;
    }
    setSelectedKeys((previous) => {
      const next = new Set(previous);
      if (allVisibleSelected) {
        paginatedItems.forEach((row) => next.delete(row.key));
      } else {
        paginatedItems.forEach((row) => next.add(row.key));
      }
      return next;
    });
  };

  const columnCount = columns.length + (enableSelection ? 1 : 0);
  const hasData = sortedItems.length > 0;

  const shouldShowToolbar = enableExport || (enableSelection && selectedItems.length > 0);

  const handleExportCsv = () => {
    exportToCsv(columns, sortedItems.map((row) => row.item), exportFileName);
  };

  const handleExportExcel = () => {
    exportToExcel(columns, sortedItems.map((row) => row.item), exportFileName);
  };

  return (
    <div className={styles.tableContainer}>
      {shouldShowToolbar ? (
        <div className={styles.toolbar}>
          {enableSelection && selectedItems.length > 0 ? (
            <div className={styles.selectionArea}>
              <span className={styles.selectionSummary}>
                {selectedItems.length} item
                {selectedItems.length > 1 ? "s" : ""} selecionado
                {selectedItems.length > 1 ? "s" : ""}
              </span>
              {selectionActions ? selectionActions(selectedItems, clearSelection) : null}
              <button type="button" className={styles.clearSelectionButton} onClick={clearSelection}>
                Limpar seleção
              </button>
            </div>
          ) : null}

          {enableExport ? (
            <div className={styles.exportActions}>
              <button type="button" className={styles.exportButton} onClick={handleExportCsv}>
                Exportar CSV
              </button>
              <button type="button" className={styles.exportButton} onClick={handleExportExcel}>
                Exportar Excel
              </button>
            </div>
          ) : null}
        </div>
      ) : null}

      <div className={styles.tableWrapper}>
        <table>
          <thead>
          <tr>
            {enableSelection ? (
              <th className={styles.selectionHeader}>
                <input
                  type="checkbox"
                  aria-label="Selecionar todos"
                  checked={allVisibleSelected}
                  onChange={handleToggleAllVisible}
                />
              </th>
            ) : null}
            {columns.map((column) => {
              const sorted = isColumnSorted(column);
              return (
                <th
                  key={column.header}
                  style={{ textAlign: column.align ?? "left", width: column.width }}
                  className={column.sortable && enableSorting ? styles.sortableHeader : undefined}
                  onClick={() => handleSort(column)}
                >
                  <span className={styles.headerContent}>
                    {column.header}
                    {column.sortable && enableSorting ? (
                      <span
                        className={sorted ? styles.sortIndicatorActive : styles.sortIndicator}
                        aria-hidden="true"
                      >
                        {sorted ? (sortState?.direction === "asc" ? "▲" : "▼") : "▲"}
                      </span>
                    ) : null}
                  </span>
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {!hasData ? (
            <tr>
              <td className={styles.emptyState} colSpan={columnCount}>
                {emptyMessage}
              </td>
            </tr>
          ) : (
            paginatedItems.map(({ item, key }) => {
              const isSelected = enableSelection ? selectedKeys.has(key) : false;
              return (
                <tr key={key} className={isSelected ? styles.selectedRow : undefined}>
                  {enableSelection ? (
                    <td className={styles.selectionCell}>
                      <input
                        type="checkbox"
                        aria-label="Selecionar linha"
                        checked={isSelected}
                        onChange={() => toggleRowSelection(key)}
                      />
                    </td>
                  ) : null}
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

      {enablePagination ? (
        <div className={styles.pagination}>
          <div className={styles.pageSizeControl}>
            <label>
              Itens por página
              <select
                value={pageSize}
                onChange={(event) => {
                  const nextSize = Number(event.target.value);
                  setPageSize(nextSize);
                  setCurrentPage(1);
                }}
              >
                {pageSizeOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className={styles.pageControls}>
            <button
              type="button"
              onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
              disabled={currentPage === 1}
            >
              Anterior
            </button>
            <span className={styles.pageSummary}>
              Página {currentPage} de {totalPages}
            </span>
            <button
              type="button"
              onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))}
              disabled={currentPage === totalPages}
            >
              Próxima
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
