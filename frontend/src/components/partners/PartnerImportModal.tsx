import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from "react";

import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import {
  importPartners,
  type PartnerImportSummary,
  type ImportErrorSummary,
} from "@/services/partners";

import styles from "@/components/import/ImportModal.module.css";

const REQUIRED_COLUMNS = ["parceiro", "cnpj_cpf", "telefone", "cidade", "estado"];
const OPTIONAL_COLUMNS = [
  "distribuidora",
  "email",
  "dia_pagamento",
  "banco",
  "agencia_conta",
  "pix",
  "cx_copo",
  "dez_litros",
  "vinte_litros",
  "mil_quinhentos_ml",
  "vasilhame",
];

type PartnerImportModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onCompleted: (summary: PartnerImportSummary) => Promise<void> | void;
};

export function PartnerImportModal({ isOpen, onClose, onCompleted }: PartnerImportModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [summary, setSummary] = useState<PartnerImportSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      setFile(null);
      setSummary(null);
      setError(null);
      setIsSubmitting(false);
    }
  }, [isOpen]);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const [selected] = Array.from(event.target.files ?? []);
    setFile(selected ?? null);
    setSummary(null);
    setError(null);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!file) {
      setError("Selecione um arquivo em formato CSV ou Excel.");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const result = await importPartners(file);
      setSummary(result);
      await onCompleted(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Não foi possível importar os parceiros.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const displayedErrors = useMemo<ImportErrorSummary[]>(() => {
    if (!summary?.errors?.length) {
      return [];
    }
    return summary.errors.slice(0, 20);
  }, [summary?.errors]);

  const remainingErrors = summary && summary.error_count > displayedErrors.length
    ? summary.error_count - displayedErrors.length
    : 0;

  const footerContent = summary
    ? (
        <Button type="button" onClick={onClose}>
          Concluir
        </Button>
      )
    : (
        <>
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancelar
          </Button>
          <Button
            type="submit"
            form="partner-import-form"
            isLoading={isSubmitting}
            loadingText="Importando..."
            disabled={!file}
          >
            Importar dados
          </Button>
        </>
      );

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Importar parceiros" footer={footerContent}>
      <form id="partner-import-form" className={styles.container} onSubmit={handleSubmit}>
        <section className={styles.section}>
          <div className={styles.instructions}>
            <h4>Prepare sua planilha</h4>
            <ul className={styles.instructionsList}>
              <li>Utilize arquivos <strong>.csv</strong>, <strong>.xlsx</strong> ou <strong>.xls</strong>.</li>
              <li>Garanta que a primeira linha contenha o cabeçalho das colunas.</li>
              <li>Os valores numéricos podem conter separador decimal com vírgula ou ponto.</li>
            </ul>
          </div>

          <div className={styles.section}>
            <strong>Colunas obrigatórias:</strong>
            <div className={styles.columnsList}>
              {REQUIRED_COLUMNS.map((column) => (
                <code key={column}>{column}</code>
              ))}
            </div>
          </div>

          <div className={styles.section}>
            <span>Colunas opcionais:</span>
            <div className={styles.columnsList}>
              {OPTIONAL_COLUMNS.map((column) => (
                <code key={column}>{column}</code>
              ))}
            </div>
          </div>
        </section>

        <section className={styles.fileInput}>
          <label htmlFor="partner-import-file">Arquivo da planilha</label>
          <input
            id="partner-import-file"
            type="file"
            accept=".csv, application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            onChange={handleFileChange}
          />
          <p className={styles.hint}>Substituições e atualizações são feitas com base no CPF/CNPJ informado.</p>
          {error ? <div className={styles.errorMessage}>{error}</div> : null}
        </section>

        {summary ? (
          <section className={styles.summary} aria-live="polite">
            <h4>Resultado da importação</h4>
            <div className={styles.summaryGrid}>
              <div className={styles.summaryItem}>
                <span>Linhas processadas</span>
                <span className={styles.summaryValue}>{summary.total}</span>
              </div>
              <div className={styles.summaryItem}>
                <span>Novos parceiros</span>
                <span className={styles.summaryValue}>{summary.created}</span>
              </div>
              <div className={styles.summaryItem}>
                <span>Atualizados</span>
                <span className={styles.summaryValue}>{summary.updated}</span>
              </div>
              <div className={styles.summaryItem}>
                <span>Ignorados</span>
                <span className={styles.summaryValue}>{summary.skipped}</span>
              </div>
              <div className={styles.summaryItem}>
                <span>Erros</span>
                <span className={styles.summaryValue}>{summary.error_count}</span>
              </div>
            </div>

            {displayedErrors.length > 0 ? (
              <div>
                <strong>Ocorreram erros em algumas linhas:</strong>
                <ul className={styles.errorList}>
                  {displayedErrors.map((item) => (
                    <li key={`${item.row}-${item.message}`}>
                      {item.row ? `Linha ${item.row}: ` : "Linha desconhecida: "}
                      {item.message}
                    </li>
                  ))}
                </ul>
                {remainingErrors > 0 ? (
                  <p className={styles.hint}>{`... e mais ${remainingErrors} erro(s) não exibidos.`}</p>
                ) : null}
              </div>
            ) : null}
          </section>
        ) : null}
      </form>
    </Modal>
  );
}

