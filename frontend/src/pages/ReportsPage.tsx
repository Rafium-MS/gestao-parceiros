import { useEffect, useMemo, useState } from "react";

import { ReportFilters, ReportFiltersValue } from "@/components/reports/ReportFilters";
import { Card } from "@/components/ui/Card";
import { DataTable, TableColumn } from "@/components/ui/DataTable";
import { TableSkeleton } from "@/components/ui/TableSkeleton";
import { listReportEntries, type ReportEntry } from "@/services/reports";
import { formatCurrency, formatDate } from "@/utils/formatters";
import { useToast } from "@/contexts/ToastContext";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";

import styles from "./ReportsPage.module.css";

type ReportRow = {
  marca: string;
  loja: string;
  registros: number;
  valorTotal: number;
  valor20L: number;
  valor10L: number;
  valor1500: number;
  valorCxCopo: number;
  valorVasilhame: number;
  ultimoRegistro: string;
};

const initialFilters: ReportFiltersValue = {
  period: "30d",
  status: "todos",
  channel: "todos",
  partner: "",
  referenceMonth: new Date().toISOString().slice(0, 7),
};

type DateRange = {
  startDate?: string;
  endDate?: string;
};

function areFiltersEqual(a: ReportFiltersValue, b: ReportFiltersValue) {
  return (
    a.period === b.period &&
    a.status === b.status &&
    a.channel === b.channel &&
    a.partner === b.partner &&
    a.referenceMonth === b.referenceMonth
  );
}

function resolveDateRange(filters: ReportFiltersValue): DateRange {
  const now = new Date();
  let startDate: string | undefined;
  let endDate: string | undefined;

  const todayIso = now.toISOString().slice(0, 10);
  endDate = todayIso;

  switch (filters.period) {
    case "7d": {
      const start = new Date(now);
      start.setDate(now.getDate() - 6);
      startDate = start.toISOString().slice(0, 10);
      break;
    }
    case "30d": {
      const start = new Date(now);
      start.setDate(now.getDate() - 29);
      startDate = start.toISOString().slice(0, 10);
      break;
    }
    case "90d": {
      const start = new Date(now);
      start.setDate(now.getDate() - 89);
      startDate = start.toISOString().slice(0, 10);
      break;
    }
    default:
      break;
  }

  if (filters.referenceMonth) {
    const [year, month] = filters.referenceMonth.split("-").map(Number);
    if (!Number.isNaN(year) && !Number.isNaN(month)) {
      const firstDay = new Date(year, month - 1, 1);
      const lastDay = new Date(year, month, 0);
      startDate = firstDay.toISOString().slice(0, 10);
      endDate = lastDay.toISOString().slice(0, 10);
    }
  }

  if (filters.period === "custom" && !filters.referenceMonth) {
    startDate = undefined;
    endDate = undefined;
  }

  return { startDate, endDate };
}

function buildRows(entries: ReportEntry[], filters: ReportFiltersValue): ReportRow[] {
  const partnerFilter = filters.partner.trim().toLowerCase();

  const filtered = entries.filter((entry) => {
    if (!partnerFilter) {
      return true;
    }
    return (
      entry.marca.toLowerCase().includes(partnerFilter) ||
      entry.loja.toLowerCase().includes(partnerFilter)
    );
  });

  const grouped = new Map<string, ReportRow>();

  filtered.forEach((entry) => {
    const key = `${entry.marca}::${entry.loja}`;
    const current = grouped.get(key);
    const totalEntryValue =
      entry.valor_20l + entry.valor_10l + entry.valor_1500ml + entry.valor_cx_copo + entry.valor_vasilhame;

    if (!current) {
      grouped.set(key, {
        marca: entry.marca,
        loja: entry.loja,
        registros: 1,
        valorTotal: totalEntryValue,
        valor20L: entry.valor_20l,
        valor10L: entry.valor_10l,
        valor1500: entry.valor_1500ml,
        valorCxCopo: entry.valor_cx_copo,
        valorVasilhame: entry.valor_vasilhame,
        ultimoRegistro: entry.data,
      });
      return;
    }

    current.registros += 1;
    current.valorTotal += totalEntryValue;
    current.valor20L += entry.valor_20l;
    current.valor10L += entry.valor_10l;
    current.valor1500 += entry.valor_1500ml;
    current.valorCxCopo += entry.valor_cx_copo;
    current.valorVasilhame += entry.valor_vasilhame;
    if (entry.data > current.ultimoRegistro) {
      current.ultimoRegistro = entry.data;
    }
  });

  return Array.from(grouped.values()).sort((a, b) => b.valorTotal - a.valorTotal);
}

export function ReportsPage() {
  const [filters, setFilters] = useState(initialFilters);
  const [appliedFilters, setAppliedFilters] = useState(initialFilters);
  const [entries, setEntries] = useState<ReportEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { showError } = useToast();
  const debouncedFilters = useDebouncedValue(filters, 400);

  useEffect(() => {
    setAppliedFilters((current) =>
      areFiltersEqual(current, debouncedFilters) ? current : debouncedFilters,
    );
  }, [debouncedFilters]);

  useEffect(() => {
    let active = true;
    const { startDate, endDate } = resolveDateRange(appliedFilters);
    setIsLoading(true);
    setError(null);

    listReportEntries({ startDate, endDate })
      .then((data) => {
        if (active) {
          setEntries(data);
        }
      })
      .catch((err: unknown) => {
        if (active) {
          const message = err instanceof Error ? err.message : "Não foi possível carregar os relatórios.";
          setError(message);
          setEntries([]);
          showError(message);
        }
      })
      .finally(() => {
        if (active) {
          setIsLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [appliedFilters, showError]);

  const rows = useMemo(() => buildRows(entries, appliedFilters), [entries, appliedFilters]);

  const highlights = useMemo(() => {
    if (rows.length === 0) {
      return [
        {
          label: "Registros analisados",
          value: "0",
          trend: "Ajuste os filtros para visualizar dados.",
        },
      ];
    }

    const totalRegistros = rows.reduce((total, row) => total + row.registros, 0);
    const totalReceita = rows.reduce((total, row) => total + row.valorTotal, 0);
    const ticketMedio = totalRegistros > 0 ? totalReceita / totalRegistros : 0;
    const marcasAtivas = new Set(rows.map((row) => row.marca)).size;
    const destaque = rows.reduce((maior, atual) => (atual.valorTotal > maior.valorTotal ? atual : maior), rows[0]);

    return [
      {
        label: "Registros analisados",
        value: totalRegistros.toLocaleString("pt-BR"),
        trend: `Período ${appliedFilters.period}`,
      },
      {
        label: "Receita consolidada",
        value: formatCurrency(totalReceita),
        trend: `Maior volume: ${destaque.marca} / ${destaque.loja}`,
      },
      {
        label: "Ticket médio",
        value: formatCurrency(ticketMedio),
        trend: totalRegistros > 0 ? "Baseado em registros importados" : "Sem registros no período",
      },
      {
        label: "Marcas ativas",
        value: marcasAtivas.toString(),
        trend: `${rows.length} lojas monitoradas`,
      },
    ];
  }, [appliedFilters.period, rows]);

  const columns = useMemo<TableColumn<ReportRow>[]>(
    () => [
      { header: "Marca", accessor: "marca" },
      { header: "Loja", accessor: "loja" },
      {
        header: "Registros",
        align: "right",
        render: (row) => row.registros.toLocaleString("pt-BR"),
      },
      {
        header: "Último registro",
        render: (row) => formatDate(row.ultimoRegistro),
      },
      {
        header: "Receita total",
        align: "right",
        render: (row) => formatCurrency(row.valorTotal),
      },
      {
        header: "Mix 20L",
        align: "right",
        render: (row) => formatCurrency(row.valor20L),
      },
      {
        header: "Mix 10L",
        align: "right",
        render: (row) => formatCurrency(row.valor10L),
      },
      {
        header: "Mix 1500ml",
        align: "right",
        render: (row) => formatCurrency(row.valor1500),
      },
    ],
    [],
  );

  return (
    <div className="page-content">
      <header className="page-header">
        <h1>Relatórios</h1>
        <p>Visualize métricas consolidadas das vendas registradas pelo backend em Flask.</p>
      </header>

      <div className={styles.highlights}>
        {highlights.map((item) => (
          <div key={item.label} className={styles.highlightCard}>
            <span className={styles.highlightLabel}>{item.label}</span>
            <strong className={styles.highlightValue}>{item.value}</strong>
            <span className={styles.highlightTrend}>{item.trend}</span>
          </div>
        ))}
      </div>

      <ReportFilters
        value={filters}
        onChange={setFilters}
        onApply={(value) =>
          setAppliedFilters((current) => (areFiltersEqual(current, value) ? current : value))
        }
        onReset={() => {
          setFilters(initialFilters);
          setAppliedFilters(initialFilters);
        }}
      />

      <Card title="Performance consolidada" subtitle="Dados carregados diretamente das rotas Flask.">
        {isLoading ? <TableSkeleton columns={columns.length} /> : null}

        {!isLoading && rows.length === 0 && !error ? (
          <div className={styles.emptyState}>Nenhum registro encontrado para os filtros selecionados.</div>
        ) : null}

        {!isLoading && rows.length > 0 ? (
          <DataTable
            columns={columns}
            data={rows}
            keyExtractor={(row) => `${row.marca}-${row.loja}`}
            virtualization={{ containerHeight: 520, rowHeight: 56, overscan: 6 }}
          />
        ) : null}
      </Card>
    </div>
  );
}
