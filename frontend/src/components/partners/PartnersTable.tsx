import { ChangeEvent, FormEvent, useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable, TableColumn } from "@/components/ui/DataTable";
import { FormField } from "@/components/ui/FormField";
import { Modal } from "@/components/ui/Modal";
import { TableSkeleton } from "@/components/ui/TableSkeleton";
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
import { formatCpfCnpj, formatCurrencyFromNumber, formatCurrencyInput, formatPhone } from "@/utils/masks";
import { isCpfOrCnpj, isRequired } from "@/utils/validators";

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
  cx_copo: "",
  dez_litros: "",
  vinte_litros: "",
  mil_quinhentos_ml: "",
  vasilhame: "",
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

const BRAZIL_STATE_CODES = new Set(BRAZIL_STATES.map((state) => state.value));

const PRICE_FIELDS: Array<keyof PartnerForm> = [
  "cx_copo",
  "dez_litros",
  "vinte_litros",
  "mil_quinhentos_ml",
  "vasilhame",
];

const FORM_DRAFT_STORAGE_KEY = "partners:form-draft";

function normalizeText(value: string) {
  return value.trim();
}

function parseCurrency(value: string) {
  if (!value) {
    return 0;
  }

  const normalized = value.replace(/\./g, "").replace(",", ".");
  const parsed = Number.parseFloat(normalized);
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
  const [isBulkDeleting, setIsBulkDeleting] = useState(false);
  const { isOpen, open, close } = useDisclosure();

  const fieldValidators = useMemo<
    Partial<Record<keyof PartnerForm, (value: string, currentForm: PartnerForm) => string | undefined>>
  >(
    () => ({
      parceiro: (value) => {
        if (!isRequired(value)) {
          return "Informe o nome do parceiro.";
        }
        return undefined;
      },
      cnpj_cpf: (value) => {
        if (!isRequired(value)) {
          return "Informe o CPF ou CNPJ.";
        }
        if (!isCpfOrCnpj(value)) {
          return "Informe um CPF ou CNPJ válido.";
        }
        return undefined;
      },
      cidade: (value) => {
        if (!isRequired(value)) {
          return "Informe a cidade.";
        }
        return undefined;
      },
      estado: (value) => {
        if (!isRequired(value)) {
          return "Informe a UF.";
        }

        const normalized = value.trim().toUpperCase();
        if (!BRAZIL_STATE_CODES.has(normalized)) {
          return "Selecione uma UF válida.";
        }

        return undefined;
      },
      telefone: (value) => {
        if (!isRequired(value)) {
          return "Informe um telefone de contato.";
        }

        const digits = value.replace(/\D/g, "");
        if (digits.length < 10) {
          return "Informe um telefone válido.";
        }

        return undefined;
      },
      dia_pagamento: (value) => {
        if (!value) {
          return undefined;
        }

        const day = Number(value);
        if (Number.isNaN(day) || day < 1 || day > 31) {
          return "Informe um dia entre 1 e 31.";
        }

        return undefined;
      },
    }),
    [],
  );

  const formatFieldValue = useCallback((field: keyof PartnerForm, value: string) => {
    if (field === "telefone") {
      return formatPhone(value);
    }

    if (field === "cnpj_cpf") {
      return formatCpfCnpj(value);
    }

    if (field === "estado") {
      return value.replace(/[^a-zA-Z]/g, "").slice(0, 2).toUpperCase();
    }

    if (PRICE_FIELDS.includes(field)) {
      if (!value) {
        return "";
      }
      return formatCurrencyInput(value);
    }

    return value;
  }, []);

  const handleFieldChange = useCallback(
    (field: keyof PartnerForm) => (event: ChangeEvent<HTMLInputElement>) => {
      const rawValue = event.target.value;
      setForm((current) => {
        const formattedValue = formatFieldValue(field, rawValue);
        const nextForm = { ...current, [field]: formattedValue };
        const validator = fieldValidators[field];

        if (validator) {
          const message = validator(formattedValue, nextForm);
          setErrors((currentErrors) => {
            const { global, ...rest } = currentErrors;
            const hadGlobal = global !== undefined;

            if (message) {
              if (rest[field] === message && !hadGlobal) {
                return currentErrors;
              }
              return { ...rest, [field]: message };
            }

            if (!(field in rest)) {
              return hadGlobal ? rest : currentErrors;
            }

            const { [field]: _removed, ...remaining } = rest;
            return remaining;
          });
        } else {
          setErrors((currentErrors) => {
            if (currentErrors.global === undefined) {
              return currentErrors;
            }
            const { global, ...rest } = currentErrors;
            return rest;
          });
        }

        return nextForm;
      });
    },
    [fieldValidators, formatFieldValue],
  );

  const validateField = useCallback(
    (field: keyof PartnerForm, value: string, currentForm: PartnerForm) => {
      const validator = fieldValidators[field];
      return validator ? validator(value, currentForm) : undefined;
    },
    [fieldValidators],
  );

  const validateForm = useCallback(
    (formState: PartnerForm) => {
      const fieldsToValidate: Array<keyof PartnerForm> = [
        "parceiro",
        "cnpj_cpf",
        "cidade",
        "estado",
        "telefone",
        "dia_pagamento",
      ];

      const validationErrors: FormErrors = {};
      fieldsToValidate.forEach((field) => {
        const error = validateField(field, formState[field], formState);
        if (error) {
          validationErrors[field] = error;
        }
      });

      return validationErrors;
    },
    [validateField],
  );

  const citySuggestions = useMemo(() => {
    const cities = partners
      .map((partner) => partner.cidade?.trim())
      .filter((city): city is string => Boolean(city));

    return Array.from(new Set(cities)).sort((a, b) =>
      a.localeCompare(b, "pt-BR", { sensitivity: "base" }),
    );
  }, [partners]);

  const cityDatalistId = "partner-city-options";
  const stateDatalistId = "partner-state-options";

  const loadDraft = useCallback((): PartnerForm | null => {
    if (typeof window === "undefined") {
      return null;
    }

    try {
      const stored = window.localStorage.getItem(FORM_DRAFT_STORAGE_KEY);
      if (!stored) {
        return null;
      }

      const parsed = JSON.parse(stored) as Partial<PartnerForm>;
      return { ...defaultForm, ...parsed };
    } catch (error) {
      console.error("Erro ao carregar rascunho do parceiro", error);
      return null;
    }
  }, []);

  useEffect(() => {
    if (typeof window === "undefined" || mode !== "create" || !isOpen) {
      return;
    }

    try {
      window.localStorage.setItem(FORM_DRAFT_STORAGE_KEY, JSON.stringify(form));
    } catch (error) {
      console.error("Erro ao salvar rascunho do parceiro", error);
    }
  }, [form, mode, isOpen]);

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

  const handleDelete = useCallback(async (partner: PartnerRecord) => {
    if (!window.confirm(`Deseja excluir o parceiro ${partner.parceiro}?`)) {
      return;
    }
    try {
      await deletePartner(partner.id);
      setPartners((current) => current.filter((item) => item.id !== partner.id));
      setFetchError(null);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Não foi possível excluir o parceiro.";
      setFetchError(message);
    }
  }, []);

  const handleEdit = useCallback((partner: PartnerRecord) => {
    setMode("edit");
    setEditingPartner(partner);
    setForm({
      parceiro: partner.parceiro ?? "",
      cnpj_cpf: formatCpfCnpj(partner.cnpj_cpf ?? ""),
      cidade: partner.cidade ?? "",
      estado: partner.estado ?? "",
      telefone: formatPhone(partner.telefone ?? ""),
      email: partner.email ?? "",
      distribuidora: partner.distribuidora ?? "",
      dia_pagamento: partner.dia_pagamento ? String(partner.dia_pagamento) : "",
      banco: partner.banco ?? "",
      agencia_conta: partner.agencia_conta ?? "",
      pix: partner.pix ?? "",
      cx_copo: formatCurrencyFromNumber(partner.cx_copo ?? null),
      dez_litros: formatCurrencyFromNumber(partner.dez_litros ?? null),
      vinte_litros: formatCurrencyFromNumber(partner.vinte_litros ?? null),
      mil_quinhentos_ml: formatCurrencyFromNumber(partner.mil_quinhentos_ml ?? null),
      vasilhame: formatCurrencyFromNumber(partner.vasilhame ?? null),
    });
    setErrors({});
    open();
  }, [open]);

  const handleBulkDelete = useCallback(
    async (selected: PartnerRecord[], clearSelection: () => void) => {
      if (selected.length === 0) {
        return;
      }

      const confirmationMessage =
        selected.length === 1
          ? `Deseja excluir o parceiro ${selected[0].parceiro}?`
          : `Deseja excluir ${selected.length} parceiros selecionados?`;
      if (!window.confirm(confirmationMessage)) {
        return;
      }

      setIsBulkDeleting(true);
      try {
        await Promise.all(selected.map((partner) => deletePartner(partner.id)));
        const idsToRemove = new Set(selected.map((partner) => partner.id));
        setPartners((current) => current.filter((partner) => !idsToRemove.has(partner.id)));
        setFetchError(null);
        clearSelection();
      } catch (error) {
        const message =
          error instanceof Error
            ? error.message
            : "Não foi possível excluir os parceiros selecionados.";
        setFetchError(message);
      } finally {
        setIsBulkDeleting(false);
      }
    },
    [],
  );

  const renderSelectionActions = useCallback(
    (selected: PartnerRecord[], clearSelection: () => void) => (
      <Button
        size="sm"
        variant="danger"
        onClick={() => handleBulkDelete(selected, clearSelection)}
        disabled={isBulkDeleting}
      >
        {isBulkDeleting
          ? "Excluindo..."
          : `Excluir ${selected.length > 1 ? "selecionados" : "selecionado"}`}
      </Button>
    ),
    [handleBulkDelete, isBulkDeleting],
  );

  const columns = useMemo<TableColumn<PartnerRecord>[]>(
    () => [
      { header: "Parceiro", accessor: "parceiro", sortable: true },
      { header: "Documento", accessor: "cnpj_cpf", sortable: true },
      {
        header: "Localização",
        render: (partner) => `${partner.cidade} - ${partner.estado}`,
        sortable: true,
        sortValue: (partner) => `${partner.cidade ?? ""} ${partner.estado ?? ""}`,
        exportValue: (partner) => `${partner.cidade ?? ""} - ${partner.estado ?? ""}`,
      },
      { header: "Telefone", accessor: "telefone", sortable: true },
      {
        header: "E-mail",
        render: (partner) => partner.email ?? "—",
        sortable: true,
        exportValue: (partner) => partner.email ?? "",
      },
      {
        header: "Volume total",
        align: "right",
        render: (partner) => numberFormatter.format(partner.total),
        sortable: true,
        sortValue: (partner) => partner.total,
        exportValue: (partner) => partner.total,
      },
      {
        header: "Cadastro",
        render: (partner) => (partner.created_at ? formatDate(partner.created_at) : "—"),
        sortable: true,
        sortValue: (partner) => (partner.created_at ? new Date(partner.created_at) : null),
        exportValue: (partner) => partner.created_at ?? "",
      },
      {
        header: "Ações",
        width: "160px",
        disableExport: true,
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
    [handleDelete, handleEdit],
  );

  const handleOpenCreate = () => {
    setMode("create");
    setEditingPartner(null);
    const draft = loadDraft();
    if (draft) {
      setForm(draft);
      setErrors(validateForm(draft));
    } else {
      setForm(defaultForm);
      setErrors({});
    }
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

    const validationErrors = validateForm(form);
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
        if (typeof window !== "undefined") {
          try {
            window.localStorage.removeItem(FORM_DRAFT_STORAGE_KEY);
          } catch (error) {
            console.error("Erro ao limpar rascunho do parceiro", error);
          }
        }
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
      {isLoading ? <TableSkeleton columns={columns.length} /> : null}

      {!isLoading && partners.length === 0 && !fetchError ? (
        <div className={styles.feedback}>Nenhum parceiro cadastrado até o momento.</div>
      ) : null}

      {!isLoading && partners.length > 0 ? (
        <DataTable
          columns={columns}
          data={partners}
          keyExtractor={(partner) => partner.id.toString()}
          enableSorting
          initialSort={{ columnKey: "parceiro", direction: "asc" }}
          enablePagination
          enableSelection
          selectionActions={renderSelectionActions}
          enableExport
          exportFileName="parceiros"
        />
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
            <Button
              type="submit"
              form="partner-form"
              isLoading={isSubmitting}
              loadingText="Salvando..."
            >
              {mode === "create" ? "Salvar parceiro" : "Atualizar parceiro"}
            </Button>
          </>
        }
      >
        <form id="partner-form" className={styles.modalForm} onSubmit={handleSubmit}>
          {errors.global ? <div className={styles.errorMessage}>{errors.global}</div> : null}

          <datalist id={cityDatalistId}>
            {citySuggestions.map((city) => (
              <option key={city} value={city} />
            ))}
          </datalist>
          <datalist id={stateDatalistId}>
            {BRAZIL_STATES.map((uf) => (
              <option key={uf.value} value={uf.value} label={uf.label} />
            ))}
          </datalist>

          <section className={styles.formSection}>
            <h2 className={styles.formSectionTitle}>Informações do parceiro</h2>

            <FormField label="Nome fantasia" htmlFor="partner-name" error={errors.parceiro}>
              <TextInput
                id="partner-name"
                placeholder="Ex.: Distribuidora Azul"
                value={form.parceiro}
                onChange={handleFieldChange("parceiro")}
                hasError={Boolean(errors.parceiro)}
                required
              />
            </FormField>

            <div className={styles.formRow}>
              <FormField label="CPF ou CNPJ" htmlFor="partner-cnpj" error={errors.cnpj_cpf}>
                <TextInput
                  id="partner-cnpj"
                  placeholder="00.000.000/0000-00"
                  value={form.cnpj_cpf}
                  onChange={handleFieldChange("cnpj_cpf")}
                  hasError={Boolean(errors.cnpj_cpf)}
                  inputMode="numeric"
                  required
                />
              </FormField>
              <FormField label="Telefone" htmlFor="partner-phone" error={errors.telefone}>
                <TextInput
                  id="partner-phone"
                  placeholder="(00) 0000-0000"
                  value={form.telefone}
                  onChange={handleFieldChange("telefone")}
                  hasError={Boolean(errors.telefone)}
                  inputMode="tel"
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
                  onChange={handleFieldChange("cidade")}
                  hasError={Boolean(errors.cidade)}
                  list={cityDatalistId}
                  required
                />
              </FormField>

              <FormField label="UF" htmlFor="partner-state" error={errors.estado}>
                <TextInput
                  id="partner-state"
                  placeholder="Ex.: SP"
                  value={form.estado}
                  onChange={handleFieldChange("estado")}
                  hasError={Boolean(errors.estado)}
                  list={stateDatalistId}
                  maxLength={2}
                  required
                />
              </FormField>
            </div>

            <div className={styles.formRow}>
              <FormField label="E-mail" htmlFor="partner-email">
                <TextInput
                  id="partner-email"
                  placeholder="contato@empresa.com"
                  value={form.email}
                  onChange={handleFieldChange("email")}
                  type="email"
                />
              </FormField>
              <FormField label="Distribuidora" htmlFor="partner-distributor">
                <TextInput
                  id="partner-distributor"
                  placeholder="Nome da distribuidora"
                  value={form.distribuidora}
                  onChange={handleFieldChange("distribuidora")}
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
                  onChange={handleFieldChange("dia_pagamento")}
                  hasError={Boolean(errors.dia_pagamento)}
                />
              </FormField>
              <FormField label="Banco" htmlFor="partner-bank">
                <TextInput
                  id="partner-bank"
                  value={form.banco}
                  onChange={handleFieldChange("banco")}
                />
              </FormField>
              <FormField label="Agência e conta" htmlFor="partner-account">
                <TextInput
                  id="partner-account"
                  value={form.agencia_conta}
                  onChange={handleFieldChange("agencia_conta")}
                />
              </FormField>
              <FormField label="Chave PIX" htmlFor="partner-pix">
                <TextInput
                  id="partner-pix"
                  value={form.pix}
                  onChange={handleFieldChange("pix")}
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
                  type="text"
                  value={form.cx_copo}
                  onChange={handleFieldChange("cx_copo")}
                  inputMode="decimal"
                  placeholder="0,00"
                />
              </FormField>
              <FormField label="Valor 10 litros" htmlFor="partner-dez_litros">
                <TextInput
                  id="partner-dez_litros"
                  type="text"
                  value={form.dez_litros}
                  onChange={handleFieldChange("dez_litros")}
                  inputMode="decimal"
                  placeholder="0,00"
                />
              </FormField>
              <FormField label="Valor 20 litros" htmlFor="partner-vinte_litros">
                <TextInput
                  id="partner-vinte_litros"
                  type="text"
                  value={form.vinte_litros}
                  onChange={handleFieldChange("vinte_litros")}
                  inputMode="decimal"
                  placeholder="0,00"
                />
              </FormField>
            </div>

            <div className={styles.formRow}>
              <FormField label="Valor 1500 ml" htmlFor="partner-mil_quinhentos_ml">
                <TextInput
                  id="partner-mil_quinhentos_ml"
                  type="text"
                  value={form.mil_quinhentos_ml}
                  onChange={handleFieldChange("mil_quinhentos_ml")}
                  inputMode="decimal"
                  placeholder="0,00"
                />
              </FormField>
              <FormField label="Valor vasilhame" htmlFor="partner-vasilhame">
                <TextInput
                  id="partner-vasilhame"
                  type="text"
                  value={form.vasilhame}
                  onChange={handleFieldChange("vasilhame")}
                  inputMode="decimal"
                  placeholder="0,00"
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
