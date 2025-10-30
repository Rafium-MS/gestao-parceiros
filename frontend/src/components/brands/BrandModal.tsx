import { FormEvent, useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { FormField } from "@/components/ui/FormField";
import { Modal } from "@/components/ui/Modal";
import { TextInput } from "@/components/ui/TextInput";
import { createBrand, updateBrand } from "@/services/api";
import { BrandRecord } from "@/types";

import styles from "./BrandModal.module.css";

type BrandFormErrors = {
  marca?: string;
  global?: string;
};

type BrandFormData = {
  marca: string;
  cod_disagua: string;
};

type BrandModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  editingBrand?: BrandRecord | null;
};

export function BrandModal({ isOpen, onClose, onSuccess, editingBrand }: BrandModalProps) {
  const [form, setForm] = useState<BrandFormData>({ marca: "", cod_disagua: "" });
  const [errors, setErrors] = useState<BrandFormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const mode = editingBrand ? "edit" : "create";

  useEffect(() => {
    if (isOpen) {
      if (editingBrand) {
        setForm({
          marca: editingBrand.marca,
          cod_disagua: editingBrand.cod_disagua ?? "",
        });
      } else {
        setForm({ marca: "", cod_disagua: "" });
      }
      setErrors({});
    }
  }, [isOpen, editingBrand]);

  const handleClose = () => {
    if (!isSubmitting) {
      onClose();
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrors({});

    if (!form.marca.trim()) {
      setErrors({ marca: "Informe o nome da marca." });
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = {
        marca: form.marca.trim(),
        cod_disagua: form.cod_disagua.trim() || undefined,
      };

      if (mode === "create") {
        await createBrand(payload);
      } else if (editingBrand) {
        await updateBrand(editingBrand.id, {
          ...payload,
          cod_disagua: payload.cod_disagua || null,
        });
      }

      onSuccess();
      handleClose();
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Não foi possível salvar a marca.";
      setErrors({ global: message });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={mode === "create" ? "Cadastrar nova marca" : "Editar marca"}
      footer={
        <>
          <Button variant="ghost" onClick={handleClose} type="button" disabled={isSubmitting}>
            Cancelar
          </Button>
          <Button
            type="submit"
            form="brand-form"
            isLoading={isSubmitting}
            loadingText="Salvando..."
          >
            {mode === "create" ? "Cadastrar marca" : "Atualizar marca"}
          </Button>
        </>
      }
    >
      <form id="brand-form" className={styles.form} onSubmit={handleSubmit}>
        {errors.global ? <div className={styles.errorMessage}>{errors.global}</div> : null}

        <FormField label="Nome da marca" htmlFor="brand-name" error={errors.marca}>
          <TextInput
            id="brand-name"
            value={form.marca}
            onChange={(event) => setForm((current) => ({ ...current, marca: event.target.value }))}
            hasError={Boolean(errors.marca)}
            required
            autoFocus
          />
        </FormField>

        <FormField label="Código Diságua" htmlFor="brand-code">
          <TextInput
            id="brand-code"
            value={form.cod_disagua}
            onChange={(event) =>
              setForm((current) => ({ ...current, cod_disagua: event.target.value }))
            }
            placeholder="Opcional"
          />
        </FormField>
      </form>
    </Modal>
  );
}
