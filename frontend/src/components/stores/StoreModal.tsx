import { FormEvent, useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { FormField } from "@/components/ui/FormField";
import { Modal } from "@/components/ui/Modal";
import { SelectInput } from "@/components/ui/SelectInput";
import { TextInput } from "@/components/ui/TextInput";
import { BRAZIL_STATES } from "@/constants/brazil";
import { createStore, updateStore } from "@/services/api";
import { BrandRecord, StoreRecord } from "@/types";
import { formatCurrency, parseCurrency } from "@/utils/currency";

import styles from "./StoreModal.module.css";

type StoreFormErrors = {
  marca_id?: string;
  loja?: string;
  local_entrega?: string;
  municipio?: string;
  uf?: string;
  global?: string;
};

type StoreFormData = {
  marca_id: string;
  loja: string;
  cod_disagua: string;
  local_entrega: string;
  endereco: string;
  municipio: string;
  uf: string;
  valor_20l: string;
  valor_10l: string;
  valor_1500ml: string;
  valor_cx_copo: string;
  valor_vasilhame: string;
};

const defaultForm: StoreFormData = {
  marca_id: "",
  loja: "",
  cod_disagua: "",
  local_entrega: "",
  endereco: "",
  municipio: "",
  uf: "",
  valor_20l: "",
  valor_10l: "",
  valor_1500ml: "",
  valor_cx_copo: "",
  valor_vasilhame: "",
};

type StoreModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  editingStore?: StoreRecord | null;
  brands: BrandRecord[];
  preselectedBrandId?: number;
};

export function StoreModal({
  isOpen,
  onClose,
  onSuccess,
  editingStore,
  brands,
  preselectedBrandId,
}: StoreModalProps) {
  const [form, setForm] = useState<StoreFormData>(defaultForm);
  const [errors, setErrors] = useState<StoreFormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const mode = editingStore ? "edit" : "create";

  useEffect(() => {
    if (isOpen) {
      if (editingStore) {
        setForm({
          marca_id: String(editingStore.marca_id),
          loja: editingStore.loja,
          cod_disagua: editingStore.cod_disagua ?? "",
          local_entrega: editingStore.local_entrega,
          endereco: editingStore.endereco ?? "",
          municipio: editingStore.municipio,
          uf: editingStore.uf,
          valor_20l: formatCurrency(editingStore.valor_20l),
          valor_10l: formatCurrency(editingStore.valor_10l),
          valor_1500ml: formatCurrency(editingStore.valor_1500ml),
          valor_cx_copo: formatCurrency(editingStore.valor_cx_copo),
          valor_vasilhame: formatCurrency(editingStore.valor_vasilhame),
        });
      } else {
        setForm({
          ...defaultForm,
          marca_id: preselectedBrandId ? String(preselectedBrandId) : "",
        });
      }
      setErrors({});
    }
  }, [isOpen, editingStore, preselectedBrandId]);

  const handleClose = () => {
    if (!isSubmitting) {
      onClose();
    }
  };

  const handleFieldChange = useCallback(
    (field: keyof StoreFormData) => (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      const { value } = event.target;
      
      if (field.startsWith("valor_")) {
        setForm((current) => ({ ...current, [field]: formatCurrency(parseCurrency(value)) }));
      } else {
        setForm((current) => ({ ...current, [field]: value }));
      }
    },
    [],
  );

  const computeTotal = useCallback((formData: StoreFormData): number => {
    return (
      parseCurrency(formData.valor_20l) +
      parseCurrency(formData.valor_10l) +
      parseCurrency(formData.valor_1500ml) +
      parseCurrency(formData.valor_cx_copo) +
      parseCurrency(formData.valor_vasilhame)
    );
  }, []);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrors({});

    const validationErrors: StoreFormErrors = {};
    if (!form.marca_id) {
      validationErrors.marca_id = "Selecione uma marca.";
    }
    if (!form.loja.trim()) {
      validationErrors.loja = "Informe o nome da loja.";
    }
    if (!form.local_entrega.trim()) {
      validationErrors.local_entrega = "Informe o local de entrega.";
    }
    if (!form.municipio.trim()) {
      validationErrors.municipio = "Informe o município.";
    }
    if (!form.uf) {
      validationErrors.uf = "Selecione a UF.";
    }

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = {
        marca_id: Number(form.marca_id),
        loja: form.loja.trim(),
        cod_disagua: form.cod_disagua.trim() || undefined,
        local_entrega: form.local_entrega.trim(),
        endereco: form.endereco.trim() || undefined,
        municipio: form.municipio.trim(),
        uf: form.uf,
        valor_20l: parseCurrency(form.valor_20l),
        valor_10l: parseCurrency(form.valor_10l),
        valor_1500ml: parseCurrency(form.valor_1500ml),
        valor_cx_copo: parseCurrency(form.valor_cx_copo),
        valor_vasilhame: parseCurrency(form.valor_vasilhame),
      };

      if (mode === "create") {
        await createStore(payload);
      } else if (editingStore) {
        await updateStore(editingStore.id, payload);
      }

      onSuccess();
      handleClose();
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Não foi possível salvar a loja.";
      setErrors({ global: message });
    } finally {
      setIsSubmitting(false);
    }
  };

  const orderedBrands = [...brands].sort((a, b) =>
    a.marca.localeCompare(b.marca, "pt-BR"),
  );

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={mode === "create" ? "Cadastrar nova loja" : "Editar loja"}
      footer={
        <>
          <Button variant="ghost" onClick={handleClose} type="button" disabled={isSubmitting}>
            Cancelar
          </Button>
          <Button
            type="submit"
            form="store-form"
            isLoading={isSubmitting}
            loadingText="Salvando..."
          >
            {mode === "create" ? "Cadastrar loja" : "Atualizar loja"}
          </Button>
        </>
      }
    >
      <form id="store-form" className={styles.form} onSubmit={handleSubmit}>
        {errors.global ? <div className={styles.errorMessage}>{errors.global}</div> : null}

        <section className={styles.formSection}>
          <h2 className={styles.formSectionTitle}>Informações básicas</h2>

          <FormField label="Marca" htmlFor="store-brand" error={errors.marca_id}>
            <SelectInput
              id="store-brand"
              value={form.marca_id}
              onChange={handleFieldChange("marca_id")}
              hasError={Boolean(errors.marca_id)}
              required
            >
              <option value="" disabled>
                Selecione uma marca
              </option>
              {orderedBrands.map((brand) => (
                <option key={brand.id} value={brand.id}>
                  {brand.marca}
                </option>
              ))}
            </SelectInput>
          </FormField>

          <FormField label="Nome da loja" htmlFor="store-name" error={errors.loja}>
            <TextInput
              id="store-name"
              value={form.loja}
              onChange={handleFieldChange("loja")}
              hasError={Boolean(errors.loja)}
              required
            />
          </FormField>

          <FormField label="Código Diságua" htmlFor="store-code">
            <TextInput
              id="store-code"
              value={form.cod_disagua}
              onChange={handleFieldChange("cod_disagua")}
              placeholder="Opcional"
            />
          </FormField>
        </section>

        <section className={styles.formSection}>
          <h2 className={styles.formSectionTitle}>Localização</h2>

          <FormField
            label="Local de entrega"
            htmlFor="store-delivery-location"
            error={errors.local_entrega}
          >
            <TextInput
              id="store-delivery-location"
              value={form.local_entrega}
              onChange={handleFieldChange("local_entrega")}
              hasError={Boolean(errors.local_entrega)}
              required
            />
          </FormField>

          <FormField label="Endereço" htmlFor="store-address">
            <TextInput
              id="store-address"
              value={form.endereco}
              onChange={handleFieldChange("endereco")}
              placeholder="Opcional"
            />
          </FormField>

          <div className={styles.formRow}>
            <FormField label="Município" htmlFor="store-city" error={errors.municipio}>
              <TextInput
                id="store-city"
                value={form.municipio}
                onChange={handleFieldChange("municipio")}
                hasError={Boolean(errors.municipio)}
                required
              />
            </FormField>

            <FormField label="UF" htmlFor="store-state" error={errors.uf}>
              <SelectInput
                id="store-state"
                value={form.uf}
                onChange={handleFieldChange("uf")}
                hasError={Boolean(errors.uf)}
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
        </section>

        <section className={styles.formSection}>
          <h2 className={styles.formSectionTitle}>Valores praticados</h2>

          <div className={styles.formRow}>
            <FormField label="Valor 20 litros" htmlFor="store-valor_20l">
              <TextInput
                id="store-valor_20l"
                type="text"
                value={form.valor_20l}
                onChange={handleFieldChange("valor_20l")}
                inputMode="decimal"
                placeholder="0,00"
              />
            </FormField>

            <FormField label="Valor 10 litros" htmlFor="store-valor_10l">
              <TextInput
                id="store-valor_10l"
                type="text"
                value={form.valor_10l}
                onChange={handleFieldChange("valor_10l")}
                inputMode="decimal"
                placeholder="0,00"
              />
            </FormField>
          </div>

          <div className={styles.formRow}>
            <FormField label="Valor 1500 ml" htmlFor="store-valor_1500ml">
              <TextInput
                id="store-valor_1500ml"
                type="text"
                value={form.valor_1500ml}
                onChange={handleFieldChange("valor_1500ml")}
                inputMode="decimal"
                placeholder="0,00"
              />
            </FormField>

            <FormField label="Valor CX copo" htmlFor="store-valor_cx_copo">
              <TextInput
                id="store-valor_cx_copo"
                type="text"
                value={form.valor_cx_copo}
                onChange={handleFieldChange("valor_cx_copo")}
                inputMode="decimal"
                placeholder="0,00"
              />
            </FormField>
          </div>

          <FormField label="Valor vasilhame" htmlFor="store-valor_vasilhame">
            <TextInput
              id="store-valor_vasilhame"
              type="text"
              value={form.valor_vasilhame}
              onChange={handleFieldChange("valor_vasilhame")}
              inputMode="decimal"
              placeholder="0,00"
            />
          </FormField>

          <div className={styles.totalPreview} aria-live="polite">
            Mix total: <strong>{formatCurrency(computeTotal(form))}</strong>
          </div>
        </section>
      </form>
    </Modal>
  );
}
