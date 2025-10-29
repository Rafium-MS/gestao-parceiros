import { FormEvent, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable, TableColumn } from "@/components/ui/DataTable";
import { FormField } from "@/components/ui/FormField";
import { Modal } from "@/components/ui/Modal";
import { TextInput } from "@/components/ui/TextInput";
import { useDisclosure } from "@/hooks/useDisclosure";
import { createPartner, listPartners, PartnerPayload, PartnerRecord } from "@/services/partners";
import { formatDate } from "@/utils/formatters";
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
};

type FormErrors = Partial<Record<keyof PartnerForm, string>> & {
  global?: string;
};

const defaultForm: PartnerForm = {
  parceiro: "",
  cnpj_cpf: "",
  cidade: "",
  estado: "",
  telefone: "",
  email: "",
  distribuidora: "",
};

const numberFormatter = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
});

function normalizeText(value: string) {
  return value.trim();
}

export function PartnersTable() {
  const [partners, setPartners] = useState<PartnerRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [form, setForm] = useState<PartnerForm>(defaultForm);
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
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
    ],
    [],
  );

  const handleClose = () => {
    setForm(defaultForm);
    setErrors({});
    setIsSubmitting(false);
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
    };

    setIsSubmitting(true);
    try {
      const created = await createPartner(payload);
      setPartners((current) => [created, ...current]);
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
        title="Cadastrar novo parceiro"
        footer={
          <>
            <Button variant="ghost" onClick={handleClose} type="button">
              Cancelar
            </Button>
            <Button type="submit" form="partner-form" disabled={isSubmitting}>
              {isSubmitting ? "Salvando..." : "Salvar parceiro"}
            </Button>
          </>
        }
      >
        <form id="partner-form" className={styles.modalForm} onSubmit={handleSubmit}>
          {errors.global ? <div className={styles.errorMessage}>{errors.global}</div> : null}

          <FormField label="Nome fantasia" htmlFor="partner-name" error={errors.parceiro}>
            <TextInput
              id="partner-name"
              placeholder="Ex.: Distribuidora Azul"
              value={form.parceiro}
              onChange={(event) => setForm((current) => ({ ...current, parceiro: event.target.value }))}
              hasError={Boolean(errors.parceiro)}
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
              />
            </FormField>

            <FormField label="Telefone" htmlFor="partner-phone" error={errors.telefone}>
              <TextInput
                id="partner-phone"
                placeholder="(00) 0000-0000"
                value={form.telefone}
                onChange={(event) => setForm((current) => ({ ...current, telefone: event.target.value }))}
                hasError={Boolean(errors.telefone)}
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
              />
            </FormField>

            <FormField label="UF" htmlFor="partner-state" error={errors.estado}>
              <TextInput
                id="partner-state"
                placeholder="SP"
                value={form.estado}
                onChange={(event) => setForm((current) => ({ ...current, estado: event.target.value }))}
                hasError={Boolean(errors.estado)}
              />
            </FormField>
          </div>

          <FormField label="E-mail" htmlFor="partner-email" optional>
            <TextInput
              id="partner-email"
              placeholder="contato@empresa.com"
              value={form.email}
              onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
            />
          </FormField>

          <FormField label="Distribuidora" htmlFor="partner-distributor" optional>
            <TextInput
              id="partner-distributor"
              placeholder="Nome da distribuidora"
              value={form.distribuidora}
              onChange={(event) => setForm((current) => ({ ...current, distribuidora: event.target.value }))}
            />
          </FormField>
        </form>
      </Modal>
    </Card>
  );
}
