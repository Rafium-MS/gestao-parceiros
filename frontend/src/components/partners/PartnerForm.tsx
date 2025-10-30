import {
  ChangeEvent,
  FormEvent,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import { Button } from "@/components/ui/Button";
import { FormField } from "@/components/ui/FormField";
import { Modal } from "@/components/ui/Modal";
import { TextInput } from "@/components/ui/TextInput";
import { PartnerPayload, PartnerRecord } from "@/services/partners";
import { formatCurrency } from "@/utils/formatters";
import {
  formatCpfCnpj,
  formatCurrencyFromNumber,
  formatCurrencyInput,
  formatPhone,
} from "@/utils/masks";
import { isCpfOrCnpj, isRequired } from "@/utils/validators";

import styles from "./PartnersTable.module.css";

export type PartnerFormMode = "create" | "edit";

export type PartnerFormValues = {
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

type FormErrors = Partial<Record<keyof PartnerFormValues, string>> & {
  global?: string;
};

type PartnerFormProps = {
  isOpen: boolean;
  mode: PartnerFormMode;
  onClose: () => void;
  onSubmit: (payload: PartnerPayload) => Promise<void>;
  partner?: PartnerRecord | null;
  partners: PartnerRecord[];
  isSubmitting?: boolean;
};

const defaultFormValues: PartnerFormValues = {
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

const PRICE_FIELDS: Array<keyof PartnerFormValues> = [
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

function computeTotal(form: PartnerFormValues) {
  return PRICE_FIELDS.reduce((acc, field) => acc + parseCurrency(form[field]), 0);
}

function getInitialFormValues(partner: PartnerRecord | null | undefined) {
  if (!partner) {
    return defaultFormValues;
  }

  return {
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
  } satisfies PartnerFormValues;
}

export function PartnerForm({
  isOpen,
  mode,
  onClose,
  onSubmit,
  partner,
  partners,
  isSubmitting,
}: PartnerFormProps) {
  const [form, setForm] = useState<PartnerFormValues>(defaultFormValues);
  const [errors, setErrors] = useState<FormErrors>({});
  const [internalSubmitting, setInternalSubmitting] = useState(false);

  const submitting = internalSubmitting || Boolean(isSubmitting);

  const citySuggestions = useMemo(() => {
    const cities = partners
      .map((partnerItem) => partnerItem.cidade?.trim())
      .filter((city): city is string => Boolean(city));

    return Array.from(new Set(cities)).sort((a, b) =>
      a.localeCompare(b, "pt-BR", { sensitivity: "base" }),
    );
  }, [partners]);

  const fieldValidators = useMemo<
    Partial<Record<keyof PartnerFormValues, (value: string, currentForm: PartnerFormValues) => string | undefined>>
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

  const validateField = useCallback(
    (field: keyof PartnerFormValues, value: string, currentForm: PartnerFormValues) => {
      const validator = fieldValidators[field];
      return validator ? validator(value, currentForm) : undefined;
    },
    [fieldValidators],
  );

  const validateForm = useCallback(
    (formState: PartnerFormValues) => {
      const fieldsToValidate: Array<keyof PartnerFormValues> = [
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

  const formatFieldValue = useCallback((field: keyof PartnerFormValues, value: string) => {
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
    (field: keyof PartnerFormValues) => (event: ChangeEvent<HTMLInputElement>) => {
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

            const remaining = { ...rest };
            delete remaining[field];
            return remaining;
          });
        } else {
          setErrors((currentErrors) => {
            if (currentErrors.global === undefined) {
              return currentErrors;
            }
            const rest = { ...currentErrors };
            delete rest.global;
            return rest;
          });
        }

        return nextForm;
      });
    },
    [fieldValidators, formatFieldValue],
  );

  const loadDraft = useCallback((): PartnerFormValues | null => {
    if (typeof window === "undefined") {
      return null;
    }

    try {
      const stored = window.localStorage.getItem(FORM_DRAFT_STORAGE_KEY);
      if (!stored) {
        return null;
      }

      const parsed = JSON.parse(stored) as Partial<PartnerFormValues>;
      return { ...defaultFormValues, ...parsed };
    } catch (error) {
      console.error("Erro ao carregar rascunho do parceiro", error);
      return null;
    }
  }, []);

  const clearDraft = useCallback(() => {
    if (typeof window === "undefined") {
      return;
    }

    try {
      window.localStorage.removeItem(FORM_DRAFT_STORAGE_KEY);
    } catch (error) {
      console.error("Erro ao limpar rascunho do parceiro", error);
    }
  }, []);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const initialValues = mode === "edit" ? getInitialFormValues(partner) : defaultFormValues;

    if (mode === "create") {
      const draft = loadDraft();
      if (draft) {
        setForm(draft);
        setErrors(validateForm(draft));
        return;
      }
    }

    setForm(initialValues);
    setErrors({});
  }, [isOpen, mode, partner, loadDraft, validateForm]);

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
    if (!isOpen) {
      setInternalSubmitting(false);
    }
  }, [isOpen]);

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

    setInternalSubmitting(true);
    try {
      await onSubmit(payload);
      if (mode === "create") {
        clearDraft();
      }
      onClose();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Não foi possível salvar o parceiro.";
      setErrors({ global: message });
    } finally {
      setInternalSubmitting(false);
    }
  };

  const total = useMemo(() => computeTotal(form), [form]);

  const cityDatalistId = "partner-city-options";
  const stateDatalistId = "partner-state-options";

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={mode === "create" ? "Cadastrar novo parceiro" : "Editar parceiro"}
      footer={
        <>
          <Button variant="ghost" onClick={onClose} type="button">
            Cancelar
          </Button>
          <Button type="submit" form="partner-form" isLoading={submitting} loadingText="Salvando...">
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
                required
              />
            </FormField>
          </div>

          <div className={styles.formRow}>
            <FormField label="E-mail" htmlFor="partner-email" error={errors.email}>
              <TextInput
                id="partner-email"
                placeholder="contato@empresa.com"
                value={form.email}
                onChange={handleFieldChange("email")}
                hasError={Boolean(errors.email)}
                type="email"
              />
            </FormField>
            <FormField label="Distribuidora" htmlFor="partner-distribuidora" error={errors.distribuidora}>
              <TextInput
                id="partner-distribuidora"
                placeholder="Ex.: Unidade Centro"
                value={form.distribuidora}
                onChange={handleFieldChange("distribuidora")}
                hasError={Boolean(errors.distribuidora)}
              />
            </FormField>
          </div>

          <div className={styles.formRow}>
            <FormField label="Dia de pagamento" htmlFor="partner-payday" error={errors.dia_pagamento}>
              <TextInput
                id="partner-payday"
                placeholder="Ex.: 15"
                value={form.dia_pagamento}
                onChange={handleFieldChange("dia_pagamento")}
                hasError={Boolean(errors.dia_pagamento)}
                inputMode="numeric"
              />
            </FormField>
            <FormField label="Banco" htmlFor="partner-bank" error={errors.banco}>
              <TextInput
                id="partner-bank"
                placeholder="Banco do Brasil"
                value={form.banco}
                onChange={handleFieldChange("banco")}
                hasError={Boolean(errors.banco)}
              />
            </FormField>
          </div>

          <div className={styles.formRow}>
            <FormField label="Agência e conta" htmlFor="partner-account" error={errors.agencia_conta}>
              <TextInput
                id="partner-account"
                placeholder="0000-0 / 00000-0"
                value={form.agencia_conta}
                onChange={handleFieldChange("agencia_conta")}
                hasError={Boolean(errors.agencia_conta)}
              />
            </FormField>
            <FormField label="Chave PIX" htmlFor="partner-pix" error={errors.pix}>
              <TextInput
                id="partner-pix"
                placeholder="000.000.000-00"
                value={form.pix}
                onChange={handleFieldChange("pix")}
                hasError={Boolean(errors.pix)}
              />
            </FormField>
          </div>
        </section>

        <section className={styles.formSection}>
          <h2 className={styles.formSectionTitle}>Preços praticados</h2>

          <div className={styles.formRow}>
            <FormField label="Cx. copo" htmlFor="partner-price-cx-copo" error={errors.cx_copo}>
              <TextInput
                id="partner-price-cx-copo"
                placeholder="0,00"
                value={form.cx_copo}
                onChange={handleFieldChange("cx_copo")}
                hasError={Boolean(errors.cx_copo)}
                inputMode="decimal"
              />
            </FormField>
            <FormField label="10L" htmlFor="partner-price-10l" error={errors.dez_litros}>
              <TextInput
                id="partner-price-10l"
                placeholder="0,00"
                value={form.dez_litros}
                onChange={handleFieldChange("dez_litros")}
                hasError={Boolean(errors.dez_litros)}
                inputMode="decimal"
              />
            </FormField>
          </div>

          <div className={styles.formRow}>
            <FormField label="20L" htmlFor="partner-price-20l" error={errors.vinte_litros}>
              <TextInput
                id="partner-price-20l"
                placeholder="0,00"
                value={form.vinte_litros}
                onChange={handleFieldChange("vinte_litros")}
                hasError={Boolean(errors.vinte_litros)}
                inputMode="decimal"
              />
            </FormField>
            <FormField label="1,5L" htmlFor="partner-price-1-5l" error={errors.mil_quinhentos_ml}>
              <TextInput
                id="partner-price-1-5l"
                placeholder="0,00"
                value={form.mil_quinhentos_ml}
                onChange={handleFieldChange("mil_quinhentos_ml")}
                hasError={Boolean(errors.mil_quinhentos_ml)}
                inputMode="decimal"
              />
            </FormField>
          </div>

          <div className={styles.formRow}>
            <FormField label="Vasilhame" htmlFor="partner-price-vasilhame" error={errors.vasilhame}>
              <TextInput
                id="partner-price-vasilhame"
                placeholder="0,00"
                value={form.vasilhame}
                onChange={handleFieldChange("vasilhame")}
                hasError={Boolean(errors.vasilhame)}
                inputMode="decimal"
              />
            </FormField>
          </div>

          <span className={styles.totalPreview}>Volume total: {formatCurrency(total)}</span>
        </section>
      </form>
    </Modal>
  );
}
