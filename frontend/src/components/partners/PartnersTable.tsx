import { FormEvent, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable, TableColumn } from "@/components/ui/DataTable";
import { FormField } from "@/components/ui/FormField";
import { Modal } from "@/components/ui/Modal";
import { SelectInput } from "@/components/ui/SelectInput";
import { TextInput } from "@/components/ui/TextInput";
import { useDisclosure } from "@/hooks/useDisclosure";
import {
  createPartner,
  deletePartner,
  listPartners,
  PartnerPayload,
  PartnerRecord,
  updatePartner,
} from "@/services/partners";
import { formatCurrency, formatDate } from "@/utils/formatters";
import { isCnpj, isRequired } from "@/utils/validators";

import styles from "./PartnersTable.module.css";

type PartnerForm = {
  parceiro: string;
  cnpj_cpf: string;
  cidade: string;
  estado: string;
  telefone: string;
  email: string;
  distribuidora: string;
  dia_pagamento: string;
  banco: string;
  agencia_conta: string;
  pix: string;
  cx_copo: string;
  dez_litros: string;
  vinte_litros: string;
  mil_quinhentos_ml: string;
  vasilhame: string;
};

type FormErrors = Partial<Record<keyof PartnerForm, string>> & {
  global?: string;
};

type FormMode = "create" | "edit";

const defaultForm: PartnerForm = {
  parceiro: "",
  cnpj_cpf: "",
  cidade: "",
  estado: "",
  telefone: "",
  email: "",
  distribuidora: "",
  dia_pagamento: "",
  banco: "",
  agencia_conta: "",
  pix: "",
  cx_copo: "0",
  dez_litros: "0",
  vinte_litros: "0",
  mil_quinhentos_ml: "0",
  vasilhame: "0",
};

const numberFormatter = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
});

const BRAZIL_STATES: Array<{ value: string; label: string }> = [
  { value: "AC", label: "Acre" },
  { value: "AL", label: "Alagoas" },
  { value: "AP", label: "Amapá" },
  { value: "AM", label: "Amazonas" },
  { value: "BA", label: "Bahia" },
  { value: "CE", label: "Ceará" },
  { value: "DF", label: "Distrito Federal" },
  { value: "ES", label: "Espírito Santo" },
  { value: "GO", label: "Goiás" },
  { value: "MA", label: "Maranhão" },
  { value: "MT", label: "Mato Grosso" },
  { value: "MS", label: "Mato Grosso do Sul" },
  { value: "MG", label: "Minas Gerais" },
  { value: "PA", label: "Pará" },
  { value: "PB", label: "Paraíba" },
  { value: "PR", label: "Paraná" },
  { value: "PE", label: "Pernambuco" },
  { value: "PI", label: "Piauí" },
  { value: "RJ", label: "Rio de Janeiro" },
  { value: "RN", label: "Rio Grande do Norte" },
  { value: "RS", label: "Rio Grande do Sul" },
  { value: "RO", label: "Rondônia" },
  { value: "RR", label: "Roraima" },
  { value: "SC", label: "Santa Catarina" },
  { value: "SP", label: "São Paulo" },
  { value: "SE", label: "Sergipe" },
  { value: "TO", label: "Tocantins" },
];

const PRICE_FIELDS: Array<keyof PartnerForm> = [
  "cx_copo",
  "dez_litros",
  "vinte_litros",
  "mil_quinhentos_ml",
  "vasilhame",
];

function normalizeText(value: string) {
  return value.trim();
}

function parseCurrency(value: string) {
  const parsed = Number.parseFloat(value.replace(",", "."));
  if (Number.isNaN(parsed)) {
    return 0;
  }
  return parsed;
}

function computeTotal(form: PartnerForm) {
  return PRICE_FIELDS.reduce((acc, field) => acc + parseCurrency(form[field]), 0);
}

export function PartnersTable() {
  const [partners, setPartners] = useState<PartnerRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [form, setForm] = useState<PartnerForm>(defaultForm);
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [mode, setMode] = useState<FormMode>("create");
  const [editingPartner, setEditingPartner] = useState<PartnerRecord | null>(null);
  const { isOpen, open, close } = useDisclosure();

  useEffect(() => {
    let active = true;
    setIsLoading(true);
    listPartners()
      .then((data) => {
        if (active) {
          setPartners(data);
          setFetchError(null);
        }
      })
      .catch((error: unknown) => {
        if (active) {
          const message = error instanceof Error ? error.message : "Não foi possível carregar os parceiros.";
          setFetchError(message);
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
  }, []);

  const metrics = useMemo(() => {
    if (partners.length === 0) {
      return [
        {
          label: "Parceiros cadastrados",
          value: "0",
          delta: "Cadastre novos parceiros para começar",
        },
      ];
    }

    const totalPartners = partners.length;
    const statesCovered = new Set(partners.map((partner) => partner.estado).filter(Boolean)).size;
    const contactsWithEmail = partners.filter((partner) => Boolean(partner.email)).length;
    const totalVolume = partners.reduce((total, partner) => total + partner.total, 0);
    const citiesCovered = new Set(partners.map((partner) => partner.cidade).filter(Boolean)).size;

    return [
      {
        label: "Parceiros cadastrados",
        value: totalPartners.toString(),
        delta: `${citiesCovered} cidades atendidas`,
      },
      {
        label: "Cobertura geográfica",
        value: `${statesCovered} UF${statesCovered === 1 ? "" : "s"}`,
        delta: "Expanda para novas regiões",
      },
      {
        label: "Contatos com e-mail",
        value: contactsWithEmail.toString(),
        delta:
          totalPartners > 0
            ? `${Math.round((contactsWithEmail / totalPartners) * 100)}% da base com contato digital`
            : "Atualize os cadastros",
      },
      {
        label: "Volume contratado",
        value: numberFormatter.format(totalVolume),
        delta: "Soma das categorias cadastradas",
      },
    ];
  }, [partners]);

  const columns = useMemo<TableColumn<PartnerRecord>[]>(
    () => [
      { header: "Parceiro", accessor: "parceiro" },
      { header: "Documento", accessor: "cnpj_cpf" },
      {
        header: "Localização",
        render: (partner) => `${partner.cidade} - ${partner.estado}`,
      },
      { header: "Telefone", accessor: "telefone" },
      {
        header: "E-mail",
        render: (partner) => partner.email ?? "—",
      },
      {
        header: "Volume total",
        align: "right",
        render: (partner) => numberFormatter.format(partner.total),
      },
      {
        header: "Cadastro",
        render: (partner) => (partner.created_at ? formatDate(partner.created_at) : "—"),
      },
      {
        header: "Ações",
        width: "160px",
        render: (partner) => (
          <div className={styles.tableActions}>
            <Button size="sm" variant="secondary" onClick={() => handleEdit(partner)}>
              Editar
            </Button>
            <Button size="sm" variant="danger" onClick={() => handleDelete(partner)}>
              Excluir
            </Button>
          </div>
        ),
      },
    ],
    [partners], // eslint-disable-line react-hooks/exhaustive-deps
  );

  const handleDelete = async (partner: PartnerRecord) => {
    if (!window.confirm(`Deseja excluir o parceiro ${partner.parceiro}?`)) {
      return;
    }
    try {
      await deletePartner(partner.id);
      setPartners((current) => current.filter((item) => item.id !== partner.id));
    } catch (error) {
      const message = error instanceof Error ? error.message : "Não foi possível excluir o parceiro.";
      setFetchError(message);
    }
  };

  const handleEdit = (partner: PartnerRecord) => {
    setMode("edit");
    setEditingPartner(partner);
    setForm({
      parceiro: partner.parceiro ?? "",
      cnpj_cpf: partner.cnpj_cpf ?? "",
      cidade: partner.cidade ?? "",
      estado: partner.estado ?? "",
      telefone: partner.telefone ?? "",
      email: partner.email ?? "",
      distribuidora: partner.distribuidora ?? "",
      dia_pagamento: partner.dia_pagamento ? String(partner.dia_pagamento) : "",
      banco: partner.banco ?? "",
      agencia_conta: partner.agencia_conta ?? "",
      pix: partner.pix ?? "",
      cx_copo: String(partner.cx_copo ?? 0),
      dez_litros: String(partner.dez_litros ?? 0),
      vinte_litros: String(partner.vinte_litros ?? 0),
      mil_quinhentos_ml: String(partner.mil_quinhentos_ml ?? 0),
      vasilhame: String(partner.vasilhame ?? 0),
    });
    setErrors({});
    open();
  };

  const handleOpenCreate = () => {
    setMode("create");
    setEditingPartner(null);
    setForm(defaultForm);
    setErrors({});
    open();
  };

  const handleClose = () => {
    setForm(defaultForm);
    setErrors({});
    setIsSubmitting(false);
    setEditingPartner(null);
    close();
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrors({});

    const validationErrors: FormErrors = {};

    if (!isRequired(form.parceiro)) {
      validationErrors.parceiro = "Informe o nome do parceiro.";
    }
    if (!isRequired(form.cnpj_cpf) || !isCnpj(form.cnpj_cpf)) {
      validationErrors.cnpj_cpf = "Informe um CNPJ válido.";
    }
    if (!isRequired(form.cidade)) {
      validationErrors.cidade = "Informe a cidade.";
    }
    if (!isRequired(form.estado)) {
      validationErrors.estado = "Informe a UF.";
    }
    if (!isRequired(form.telefone)) {
      validationErrors.telefone = "Informe um telefone de contato.";
    }
    if (form.dia_pagamento) {
      const day = Number(form.dia_pagamento);
      if (Number.isNaN(day) || day < 1 || day > 31) {
        validationErrors.dia_pagamento = "Informe um dia entre 1 e 31.";
      }
    }

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    const payload: PartnerPayload = {
      parceiro: normalizeText(form.parceiro),
      cnpj_cpf: normalizeText(form.cnpj_cpf),
      cidade: normalizeText(form.cidade),
      estado: normalizeText(form.estado).toUpperCase(),
      telefone: normalizeText(form.telefone),
      distribuidora: form.distribuidora ? normalizeText(form.distribuidora) : undefined,
      email: form.email ? normalizeText(form.email) : undefined,
      dia_pagamento: form.dia_pagamento ? Number(form.dia_pagamento) : undefined,
      banco: form.banco ? normalizeText(form.banco) : undefined,
      agencia_conta: form.agencia_conta ? normalizeText(form.agencia_conta) : undefined,
      pix: form.pix ? normalizeText(form.pix) : undefined,
      cx_copo: parseCurrency(form.cx_copo),
      dez_litros: parseCurrency(form.dez_litros),
      vinte_litros: parseCurrency(form.vinte_litros),
      mil_quinhentos_ml: parseCurrency(form.mil_quinhentos_ml),
      vasilhame: parseCurrency(form.vasilhame),
    };

    setIsSubmitting(true);
    try {
      if (mode === "create") {
        const created = await createPartner(payload);
        setPartners((current) => [created, ...current]);
      } else if (editingPartner) {
        const updated = await updatePartner(editingPartner.id, payload);
        setPartners((current) =>
          current.map((partner) => (partner.id === editingPartner.id ? updated : partner)),
        );
      }
      handleClose();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Não foi possível salvar o parceiro.";
      setErrors({ global: message });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card
      title="Parceiros cadastrados"
      subtitle="Acompanhe e cadastre os parceiros que fazem parte da rede de distribuição."
      actions={
        <Button onClick={handleOpenCreate} data-testid="open-partner-modal">
          Adicionar parceiro
        </Button>
      }
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

      {fetchError ? <div className={styles.errorMessage}>{fetchError}</div> : null}
      {isLoading ? <div className={styles.feedback}>Carregando parceiros...</div> : null}

      {!isLoading && partners.length === 0 && !fetchError ? (
        <div className={styles.feedback}>Nenhum parceiro cadastrado até o momento.</div>
      ) : null}

      {!isLoading && partners.length > 0 ? (
        <DataTable columns={columns} data={partners} keyExtractor={(partner) => partner.id.toString()} />
      ) : null}

      <Modal
        isOpen={isOpen}
        onClose={handleClose}
        title={mode === "create" ? "Cadastrar novo parceiro" : "Editar parceiro"}
        footer={
          <>
            <Button variant="ghost" onClick={handleClose} type="button">
              Cancelar
            </Button>
            <Button type="submit" form="partner-form" disabled={isSubmitting}>
              {isSubmitting ? "Salvando..." : mode === "create" ? "Salvar parceiro" : "Atualizar parceiro"}
            </Button>
          </>
        }
      >
        <form id="partner-form" className={styles.modalForm} onSubmit={handleSubmit}>
          {errors.global ? <div className={styles.errorMessage}>{errors.global}</div> : null}

          <section className={styles.formSection}>
            <h2 className={styles.formSectionTitle}>Informações do parceiro</h2>

            <FormField label="Nome fantasia" htmlFor="partner-name" error={errors.parceiro}>
              <TextInput
                id="partner-name"
                placeholder="Ex.: Distribuidora Azul"
                value={form.parceiro}
                onChange={(event) => setForm((current) => ({ ...current, parceiro: event.target.value }))}
                hasError={Boolean(errors.parceiro)}
                required
              />
            </FormField>

            <div className={styles.formRow}>
              <FormField label="CNPJ" htmlFor="partner-cnpj" error={errors.cnpj_cpf}>
                <TextInput
                  id="partner-cnpj"
                  placeholder="00.000.000/0000-00"
                  value={form.cnpj_cpf}
                  onChange={(event) => setForm((current) => ({ ...current, cnpj_cpf: event.target.value }))}
                  hasError={Boolean(errors.cnpj_cpf)}
                  required
                />
              </FormField>
              <FormField label="Telefone" htmlFor="partner-phone" error={errors.telefone}>
                <TextInput
                  id="partner-phone"
                  placeholder="(00) 0000-0000"
                  value={form.telefone}
                  onChange={(event) => setForm((current) => ({ ...current, telefone: event.target.value }))}
                  hasError={Boolean(errors.telefone)}
                  required
                />
              </FormField>
            </div>

            <div className={styles.formRow}>
              <FormField label="Cidade" htmlFor="partner-city" error={errors.cidade}>
                <TextInput
                  id="partner-city"
                  placeholder="Ex.: São Paulo"
                  value={form.cidade}
                  onChange={(event) => setForm((current) => ({ ...current, cidade: event.target.value }))}
                  hasError={Boolean(errors.cidade)}
                  required
                />
              </FormField>

              <FormField label="UF" htmlFor="partner-state" error={errors.estado}>
                <SelectInput
                  id="partner-state"
                  value={form.estado}
                  onChange={(event) => setForm((current) => ({ ...current, estado: event.target.value }))}
                  hasError={Boolean(errors.estado)}
                  required
                >
                  <option value="" disabled>
                    Selecione
                  </option>
                  {BRAZIL_STATES.map((uf) => (
                    <option key={uf.value} value={uf.value}>
                      {uf.label}
                    </option>
                  ))}
                </SelectInput>
              </FormField>
            </div>

            <div className={styles.formRow}>
              <FormField label="E-mail" htmlFor="partner-email">
                <TextInput
                  id="partner-email"
                  placeholder="contato@empresa.com"
                  value={form.email}
                  onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
                  type="email"
                />
              </FormField>
              <FormField label="Distribuidora" htmlFor="partner-distributor">
                <TextInput
                  id="partner-distributor"
                  placeholder="Nome da distribuidora"
                  value={form.distribuidora}
                  onChange={(event) => setForm((current) => ({ ...current, distribuidora: event.target.value }))}
                />
              </FormField>
            </div>
          </section>

          <section className={styles.formSection}>
            <h2 className={styles.formSectionTitle}>Informações financeiras</h2>

            <div className={styles.formRow}>
              <FormField label="Dia do pagamento" htmlFor="partner-payday" error={errors.dia_pagamento}>
                <TextInput
                  id="partner-payday"
                  type="number"
                  min={1}
                  max={31}
                  value={form.dia_pagamento}
                  onChange={(event) => setForm((current) => ({ ...current, dia_pagamento: event.target.value }))}
                  hasError={Boolean(errors.dia_pagamento)}
                />
              </FormField>
              <FormField label="Banco" htmlFor="partner-bank">
                <TextInput
                  id="partner-bank"
                  value={form.banco}
                  onChange={(event) => setForm((current) => ({ ...current, banco: event.target.value }))}
                />
              </FormField>
              <FormField label="Agência e conta" htmlFor="partner-account">
                <TextInput
                  id="partner-account"
                  value={form.agencia_conta}
                  onChange={(event) => setForm((current) => ({ ...current, agencia_conta: event.target.value }))}
                />
              </FormField>
              <FormField label="Chave PIX" htmlFor="partner-pix">
                <TextInput
                  id="partner-pix"
                  value={form.pix}
                  onChange={(event) => setForm((current) => ({ ...current, pix: event.target.value }))}
                />
              </FormField>
            </div>
          </section>

          <section className={styles.formSection}>
            <h2 className={styles.formSectionTitle}>Mix de produtos</h2>

            <div className={styles.formRow}>
              <FormField label="Valor CX Copo" htmlFor="partner-cx_copo">
                <TextInput
                  id="partner-cx_copo"
                  type="number"
                  min={0}
                  step="0.01"
                  value={form.cx_copo}
                  onChange={(event) => setForm((current) => ({ ...current, cx_copo: event.target.value }))}
                />
              </FormField>
              <FormField label="Valor 10 litros" htmlFor="partner-dez_litros">
                <TextInput
                  id="partner-dez_litros"
                  type="number"
                  min={0}
                  step="0.01"
                  value={form.dez_litros}
                  onChange={(event) => setForm((current) => ({ ...current, dez_litros: event.target.value }))}
                />
              </FormField>
              <FormField label="Valor 20 litros" htmlFor="partner-vinte_litros">
                <TextInput
                  id="partner-vinte_litros"
                  type="number"
                  min={0}
                  step="0.01"
                  value={form.vinte_litros}
                  onChange={(event) => setForm((current) => ({ ...current, vinte_litros: event.target.value }))}
                />
              </FormField>
            </div>

            <div className={styles.formRow}>
              <FormField label="Valor 1500 ml" htmlFor="partner-mil_quinhentos_ml">
                <TextInput
                  id="partner-mil_quinhentos_ml"
                  type="number"
                  min={0}
                  step="0.01"
                  value={form.mil_quinhentos_ml}
                  onChange={(event) => setForm((current) => ({ ...current, mil_quinhentos_ml: event.target.value }))}
                />
              </FormField>
              <FormField label="Valor vasilhame" htmlFor="partner-vasilhame">
                <TextInput
                  id="partner-vasilhame"
                  type="number"
                  min={0}
                  step="0.01"
                  value={form.vasilhame}
                  onChange={(event) => setForm((current) => ({ ...current, vasilhame: event.target.value }))}
                />
              </FormField>
            </div>

            <div className={styles.totalPreview} aria-live="polite">
              Total estimado: <strong>{formatCurrency(computeTotal(form))}</strong>
            </div>
          </section>
        </form>
      </Modal>
    </Card>
  );
}
