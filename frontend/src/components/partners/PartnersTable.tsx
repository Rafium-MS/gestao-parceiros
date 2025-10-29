import { FormEvent, useMemo, useState } from "react";

import { Badge, BadgeTone } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable, TableColumn } from "@/components/ui/DataTable";
import { FormField } from "@/components/ui/FormField";
import { Modal } from "@/components/ui/Modal";
import { SelectInput } from "@/components/ui/SelectInput";
import { TextInput } from "@/components/ui/TextInput";
import { useDisclosure } from "@/hooks/useDisclosure";
import { formatCurrency, formatDate, formatPercentage } from "@/utils/formatters";
import { isCnpj, isRequired } from "@/utils/validators";

import styles from "./PartnersTable.module.css";

type PartnerStatus = "Ativo" | "Pendente" | "Suspenso";

type Partner = {
  id: string;
  name: string;
  cnpj: string;
  segment: string;
  status: PartnerStatus;
  lastSale: string;
  revenue: number;
  completeness: number;
};

type PartnerForm = {
  name: string;
  cnpj: string;
  segment: string;
  status: PartnerStatus;
};

const initialPartners: Partner[] = [
  {
    id: "P-001",
    name: "Rio Água Distribuidora",
    cnpj: "12.345.678/0001-99",
    segment: "Atacado",
    status: "Ativo",
    lastSale: "2023-12-18",
    revenue: 325_500,
    completeness: 92,
  },
  {
    id: "P-002",
    name: "Nordeste Bebidas LTDA",
    cnpj: "98.765.432/0001-55",
    segment: "Food Service",
    status: "Pendente",
    lastSale: "2023-11-30",
    revenue: 148_200,
    completeness: 68,
  },
  {
    id: "P-003",
    name: "Aqua Premium Comercial",
    cnpj: "11.222.333/0001-44",
    segment: "Varejo",
    status: "Ativo",
    lastSale: "2023-12-02",
    revenue: 210_890,
    completeness: 84,
  },
  {
    id: "P-004",
    name: "Grupo Fonte Clara",
    cnpj: "88.999.777/0001-10",
    segment: "Exportação",
    status: "Suspenso",
    lastSale: "2023-10-11",
    revenue: 87_400,
    completeness: 54,
  },
];

const statusTone: Record<PartnerStatus, BadgeTone> = {
  Ativo: "success",
  Pendente: "warning",
  Suspenso: "danger",
};

const defaultForm: PartnerForm = {
  name: "",
  cnpj: "",
  segment: "Atacado",
  status: "Ativo",
};

export function PartnersTable() {
  const [partners, setPartners] = useState(initialPartners);
  const [form, setForm] = useState(defaultForm);
  const [errors, setErrors] = useState<Partial<Record<keyof PartnerForm, string>>>({});

  const { isOpen, open, close } = useDisclosure();

  const metrics = useMemo(() => {
    const activeCount = partners.filter((partner) => partner.status === "Ativo").length;
    const pendingCount = partners.filter((partner) => partner.status === "Pendente").length;
    const totalRevenue = partners.reduce((total, partner) => total + partner.revenue, 0);
    const averageCompleteness = partners.reduce((total, partner) => total + partner.completeness, 0) / partners.length;

    return [
      {
        label: "Parceiros ativos",
        value: activeCount,
        delta: "+12% vs mês anterior",
      },
      {
        label: "Pendentes de integração",
        value: pendingCount,
        delta: "-3% esta semana",
      },
      {
        label: "Receita consolidada",
        value: formatCurrency(totalRevenue),
        delta: "+8% em 30 dias",
      },
      {
        label: "Dados completos",
        value: formatPercentage(averageCompleteness / 100, "pt-BR", 0),
        delta: "Meta: 95%",
      },
    ];
  }, [partners]);

  const columns: TableColumn<Partner>[] = useMemo(
    () => [
      { header: "Parceiro", accessor: "name" },
      { header: "CNPJ", accessor: "cnpj" },
      { header: "Segmento", accessor: "segment" },
      {
        header: "Status",
        render: (partner) => <Badge tone={statusTone[partner.status]}>{partner.status}</Badge>,
      },
      {
        header: "Última venda",
        render: (partner) => formatDate(partner.lastSale),
      },
      {
        header: "Receita (30d)",
        align: "right",
        render: (partner) => formatCurrency(partner.revenue),
      },
      {
        header: "Cadastro",
        render: (partner) => (
          <div>
            <div className={styles.progressBar}>
              <span className={styles.progressValue} style={{ width: `${partner.completeness}%` }} />
            </div>
            <small>{partner.completeness}%</small>
          </div>
        ),
      },
    ],
    [],
  );

  const handleClose = () => {
    setForm(defaultForm);
    setErrors({});
    close();
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const validationErrors: Partial<Record<keyof PartnerForm, string>> = {};
    if (!isRequired(form.name)) {
      validationErrors.name = "Informe o nome do parceiro";
    }
    if (!isRequired(form.cnpj) || !isCnpj(form.cnpj)) {
      validationErrors.cnpj = "Informe um CNPJ válido";
    }
    if (!isRequired(form.segment)) {
      validationErrors.segment = "Informe o segmento";
    }

    setErrors(validationErrors);

    if (Object.keys(validationErrors).length > 0) {
      return;
    }

    const newPartner: Partner = {
      id: `P-${String(partners.length + 1).padStart(3, "0")}`,
      name: form.name,
      cnpj: form.cnpj,
      segment: form.segment,
      status: form.status,
      lastSale: new Date().toISOString(),
      revenue: 0,
      completeness: 45,
    };

    setPartners((current) => [newPartner, ...current]);
    handleClose();
  };

  return (
    <Card
      title="Parceiros cadastrados"
      subtitle="Acompanhe a maturidade comercial e operacional dos parceiros ativos."
      actions={<Button onClick={open}>Adicionar parceiro</Button>}
    >
      <div className={styles.metrics}>
        {metrics.map((metric) => (
          <div key={metric.label} className={styles.metricCard}>
            <span className={styles.metricLabel}>{metric.label}</span>
            <strong className={styles.metricValue}>{metric.value}</strong>
            <span className={styles.metricDelta}>{metric.delta}</span>
          </div>
        ))}
      </div>

      <DataTable columns={columns} data={partners} keyExtractor={(partner) => partner.id} />

      <Modal
        isOpen={isOpen}
        onClose={handleClose}
        title="Cadastrar novo parceiro"
        footer={
          <>
            <Button variant="ghost" onClick={handleClose} type="button">
              Cancelar
            </Button>
            <Button type="submit" form="partner-form">
              Salvar parceiro
            </Button>
          </>
        }
      >
        <form id="partner-form" className={styles.modalForm} onSubmit={handleSubmit}>
          <FormField label="Nome fantasia" htmlFor="partner-name" error={errors.name}>
            <TextInput
              id="partner-name"
              placeholder="Ex.: Distribuidora Azul"
              value={form.name}
              onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
              hasError={Boolean(errors.name)}
            />
          </FormField>

          <div className={styles.formRow}>
            <FormField label="CNPJ" htmlFor="partner-cnpj" error={errors.cnpj}>
              <TextInput
                id="partner-cnpj"
                placeholder="00.000.000/0000-00"
                value={form.cnpj}
                onChange={(event) => setForm((current) => ({ ...current, cnpj: event.target.value }))}
                hasError={Boolean(errors.cnpj)}
              />
            </FormField>

            <FormField label="Segmento" htmlFor="partner-segment" error={errors.segment}>
              <TextInput
                id="partner-segment"
                placeholder="Ex.: Varejo"
                value={form.segment}
                onChange={(event) => setForm((current) => ({ ...current, segment: event.target.value }))}
                hasError={Boolean(errors.segment)}
              />
            </FormField>
          </div>

          <FormField label="Status operacional" htmlFor="partner-status">
            <SelectInput
              id="partner-status"
              value={form.status}
              onChange={(event) =>
                setForm((current) => ({ ...current, status: event.target.value as PartnerStatus }))
              }
            >
              <option value="Ativo">Ativo</option>
              <option value="Pendente">Pendente</option>
              <option value="Suspenso">Suspenso</option>
            </SelectInput>
          </FormField>
        </form>
      </Modal>
    </Card>
  );
}
