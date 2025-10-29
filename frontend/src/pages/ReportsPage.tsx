import { useMemo, useState } from "react";

import { ReportFilters, ReportFiltersValue } from "@/components/reports/ReportFilters";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { DataTable, TableColumn } from "@/components/ui/DataTable";
import { formatCurrency, formatPercentage } from "@/utils/formatters";

import styles from "./ReportsPage.module.css";

type ReportRow = {
  partner: string;
  channel: ReportFiltersValue["channel"];
  status: ReportFiltersValue["status"];
  orders: number;
  revenue: number;
  ticket: number;
  growth: number;
  conversion: number;
};

const channelLabels: Record<ReportFiltersValue["channel"], string> = {
  todos: "Todos",
  varejo: "Varejo físico",
  marketplace: "Marketplace",
  food_service: "Food service",
};

const mockRows: ReportRow[] = [
  {
    partner: "Rio Água Distribuidora",
    channel: "varejo",
    status: "ativos",
    orders: 186,
    revenue: 212_450,
    ticket: 1_142,
    growth: 0.18,
    conversion: 0.32,
  },
  {
    partner: "Nordeste Bebidas LTDA",
    channel: "food_service",
    status: "pendentes",
    orders: 98,
    revenue: 134_280,
    ticket: 1_370,
    growth: 0.07,
    conversion: 0.28,
  },
  {
    partner: "Aqua Premium Comercial",
    channel: "marketplace",
    status: "ativos",
    orders: 242,
    revenue: 295_740,
    ticket: 1_222,
    growth: 0.23,
    conversion: 0.36,
  },
  {
    partner: "Grupo Fonte Clara",
    channel: "varejo",
    status: "suspensos",
    orders: 41,
    revenue: 52_900,
    ticket: 1_290,
    growth: -0.12,
    conversion: 0.19,
  },
  {
    partner: "Sul Água Partners",
    channel: "marketplace",
    status: "ativos",
    orders: 158,
    revenue: 174_300,
    ticket: 1_103,
    growth: 0.11,
    conversion: 0.31,
  },
];

const initialFilters: ReportFiltersValue = {
  period: "30d",
  status: "todos",
  channel: "todos",
  partner: "",
  referenceMonth: new Date().toISOString().slice(0, 7),
};

export function ReportsPage() {
  const [filters, setFilters] = useState(initialFilters);
  const [appliedFilters, setAppliedFilters] = useState(initialFilters);

  const filteredRows = useMemo(() => {
    return mockRows.filter((row) => {
      const matchesChannel =
        appliedFilters.channel === "todos" || row.channel === appliedFilters.channel;
      const matchesStatus = appliedFilters.status === "todos" || row.status === appliedFilters.status;
      const matchesPartner =
        appliedFilters.partner.length === 0 ||
        row.partner.toLowerCase().includes(appliedFilters.partner.toLowerCase());

      return matchesChannel && matchesStatus && matchesPartner;
    });
  }, [appliedFilters]);

  const highlights = useMemo(() => {
    const orders = filteredRows.reduce((total, row) => total + row.orders, 0);
    const revenue = filteredRows.reduce((total, row) => total + row.revenue, 0);
    const avgTicket = orders > 0 ? revenue / orders : 0;
    const avgConversion =
      filteredRows.length > 0
        ? filteredRows.reduce((total, row) => total + row.conversion, 0) / filteredRows.length
        : 0;
    const avgGrowth =
      filteredRows.length > 0
        ? filteredRows.reduce((total, row) => total + row.growth, 0) / filteredRows.length
        : 0;

    return [
      {
        label: "Pedidos registrados",
        value: orders.toLocaleString("pt-BR"),
        trend: formatPercentage(avgGrowth, "pt-BR", 0),
        trendTone: avgGrowth >= 0 ? styles.trendUp : styles.trendDown,
      },
      {
        label: "Receita gerada",
        value: formatCurrency(revenue),
        trend: `${avgGrowth >= 0 ? "+" : ""}${(avgGrowth * 100).toFixed(1)}% vs período",
        trendTone: avgGrowth >= 0 ? styles.trendUp : styles.trendDown,
      },
      {
        label: "Ticket médio",
        value: formatCurrency(avgTicket),
        trend: avgTicket > 0 ? "Ticket médio ponderado" : "Sem pedidos",
        trendTone: styles.trendUp,
      },
      {
        label: "Conversão",
        value: formatPercentage(avgConversion),
        trend: avgConversion >= 0.3 ? "Acima da meta" : "Abaixo da meta",
        trendTone: avgConversion >= 0.3 ? styles.trendUp : styles.trendDown,
      },
    ];
  }, [filteredRows]);

  const columns: TableColumn<ReportRow>[] = useMemo(
    () => [
      { header: "Parceiro", accessor: "partner" },
      {
        header: "Canal",
        render: (row) => channelLabels[row.channel],
      },
      {
        header: "Pedidos",
        align: "right",
        render: (row) => row.orders.toLocaleString("pt-BR"),
      },
      {
        header: "Receita",
        align: "right",
        render: (row) => formatCurrency(row.revenue),
      },
      {
        header: "Ticket médio",
        align: "right",
        render: (row) => formatCurrency(row.ticket),
      },
      {
        header: "Crescimento",
        render: (row) => (
          <Badge tone={row.growth >= 0 ? "success" : "danger"}>{formatPercentage(row.growth)}</Badge>
        ),
      },
      {
        header: "Conversão",
        render: (row) => formatPercentage(row.conversion),
      },
    ],
    [],
  );

  return (
    <div>
      <header className="page-header">
        <h1>Relatórios</h1>
        <p>Visualize métricas detalhadas de marcas, volume de vendas e desempenho operacional.</p>
      </header>

      <div className={styles.highlights}>
        {highlights.map((item) => (
          <div key={item.label} className={styles.highlightCard}>
            <span className={styles.highlightLabel}>{item.label}</span>
            <strong className={styles.highlightValue}>{item.value}</strong>
            <span className={[styles.highlightTrend, item.trendTone].join(" ")}>{item.trend}</span>
          </div>
        ))}
      </div>

      <ReportFilters
        value={filters}
        onChange={setFilters}
        onApply={(value) => setAppliedFilters(value)}
        onReset={() => {
          setFilters(initialFilters);
          setAppliedFilters(initialFilters);
        }}
      />

      <Card title="Performance consolidada" subtitle="Dados mockados para orientar o desenvolvimento dos gráficos.">
        <DataTable columns={columns} data={filteredRows} keyExtractor={(row) => row.partner} />
      </Card>
    </div>
  );
}
