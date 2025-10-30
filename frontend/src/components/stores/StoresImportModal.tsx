import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from "react";

import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import {
  importBrandsAndStores,
  type BrandStoreImportSummary,
} from "@/services/brands";
import { type ImportErrorSummary } from "@/services/partners";

import styles from "@/components/import/ImportModal.module.css";

const BRAND_REQUIRED_COLUMNS = ["marca"];
const BRAND_OPTIONAL_COLUMNS = ["cod_disagua"];
const STORE_REQUIRED_COLUMNS = ["loja", "local_entrega", "municipio", "uf"];
const STORE_OPTIONAL_COLUMNS = [
  "cod_disagua",
  "endereco",
  "valor_20l",
  "valor_10l",
  "valor_1500ml",
  "valor_cx_copo",
  "valor_vasilhame",
];

type StoresImportModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onCompleted: (summary: BrandStoreImportSummary) => Promise<void> | void;
};

export function StoresImportModal({ isOpen, onClose, onCompleted }: StoresImportModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [summary, setSummary] = useState<BrandStoreImportSummary | null>(null);
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
      const result = await importBrandsAndStores(file);
      setSummary(result);
      await onCompleted(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Não foi possível importar marcas e lojas.";
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
            form="stores-import-form"
            isLoading={isSubmitting}
            loadingText="Importando..."
            disabled={!file}
          >
            Importar dados
          </Button>
        </>
      );

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Importar marcas e lojas" footer={footerContent}>
      <form id="stores-import-form" className={styles.container} onSubmit={handleSubmit}>
        <section className={styles.section}>
          <div className={styles.instructions}>
            <h4>Antes de importar</h4>
            <ul className={styles.instructionsList}>
              <li>Envie arquivos <strong>.csv</strong>, <strong>.xlsx</strong> ou <strong>.xls</strong>.</li>
              <li>Cada linha deve informar ao menos a coluna <code>marca</code>.</li>
              <li>Preencha as colunas de loja apenas quando desejar cadastrar ou atualizar pontos de venda.</li>
            </ul>
          </div>

          <div className={styles.section}>
            <strong>Colunas da marca:</strong>
            <div className={styles.columnsList}>
              {BRAND_REQUIRED_COLUMNS.map((column) => (
                <code key={column}>{column}</code>
              ))}
              {BRAND_OPTIONAL_COLUMNS.map((column) => (
                <code key={column}>{column}</code>
              ))}
            </div>
          </div>

          <div className={styles.section}>
            <strong>Colunas da loja</strong>
            <span className={styles.hint}>Use quando desejar criar ou atualizar lojas vinculadas à marca.</span>
            <div className={styles.columnsList}>
              {STORE_REQUIRED_COLUMNS.map((column) => (
                <code key={`required-${column}`}>{column}</code>
              ))}
              {STORE_OPTIONAL_COLUMNS.map((column) => (
                <code key={`optional-${column}`}>{column}</code>
              ))}
            </div>
          </div>
        </section>

        <section className={styles.fileInput}>
          <label htmlFor="stores-import-file">Arquivo da planilha</label>
          <input
            id="stores-import-file"
            type="file"
            accept=".csv, application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            onChange={handleFileChange}
          />
          <p className={styles.hint}>
            Marcas existentes são reconhecidas pelo nome ou pelo código Diságua quando informado.
          </p>
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
                <span>Marcas criadas</span>
                <span className={styles.summaryValue}>{summary.created_brands}</span>
              </div>
              <div className={styles.summaryItem}>
                <span>Marcas atualizadas</span>
                <span className={styles.summaryValue}>{summary.updated_brands}</span>
              </div>
              <div className={styles.summaryItem}>
                <span>Lojas criadas</span>
                <span className={styles.summaryValue}>{summary.created_stores}</span>
              </div>
              <div className={styles.summaryItem}>
                <span>Lojas atualizadas</span>
                <span className={styles.summaryValue}>{summary.updated_stores}</span>
              </div>
              <div className={styles.summaryItem}>
                <span>Registros ignorados</span>
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

