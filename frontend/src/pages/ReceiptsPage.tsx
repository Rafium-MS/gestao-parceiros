import { ChangeEvent, DragEvent, FormEvent, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable, TableColumn } from "@/components/ui/DataTable";
import { FormField } from "@/components/ui/FormField";
import { Modal } from "@/components/ui/Modal";
import { SelectInput } from "@/components/ui/SelectInput";
import { TextInput } from "@/components/ui/TextInput";
import { listBrands, type BrandRecord } from "@/services/brands";
import {
  listReceipts,
  type ReceiptRecord,
  updateReceipt,
  uploadReceipts,
} from "@/services/receipts";
import { formatDate } from "@/utils/formatters";

import styles from "./ReceiptsPage.module.css";

type UploadStep = 1 | 2 | 3 | 4;

type PreviewFile = {
  file: File;
  previewUrl: string;
};

type EditFormState = {
  filename: string;
  brand_id: string;
};

type EditFormErrors = {
  filename?: string;
  global?: string;
};

function formatSize(size: number) {
  const megabytes = size / (1024 * 1024);
  if (megabytes >= 1) {
    return `${megabytes.toFixed(2)} MB`;
  }
  const kilobytes = size / 1024;
  return `${kilobytes.toFixed(1)} KB`;
}

export function ReceiptsPage() {
  const [step, setStep] = useState<UploadStep>(1);
  const [brands, setBrands] = useState<BrandRecord[]>([]);
  const [brandFilter, setBrandFilter] = useState<string>("");
  const [selectedFiles, setSelectedFiles] = useState<PreviewFile[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<string>("");
  const [receipts, setReceipts] = useState<ReceiptRecord[]>([]);
  const [isLoadingReceipts, setIsLoadingReceipts] = useState(false);
  const [receiptsError, setReceiptsError] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [editReceipt, setEditReceipt] = useState<ReceiptRecord | null>(null);
  const [editForm, setEditForm] = useState<EditFormState>({ filename: "", brand_id: "" });
  const [editErrors, setEditErrors] = useState<EditFormErrors>({});
  const [isSavingEdit, setIsSavingEdit] = useState(false);

  useEffect(() => {
    let active = true;
    listBrands()
      .then((data) => {
        if (active) {
          setBrands(data);
        }
      })
      .catch(() => {
        // falhas ao carregar marcas não impedem o fluxo de upload
      });

    loadReceipts();

    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    return () => {
      selectedFiles.forEach((preview) => URL.revokeObjectURL(preview.previewUrl));
    };
  }, [selectedFiles]);

  const loadReceipts = () => {
    setIsLoadingReceipts(true);
    setReceiptsError(null);
    listReceipts()
      .then((data) => {
        setReceipts(data);
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : "Não foi possível carregar os comprovantes.";
        setReceiptsError(message);
        setReceipts([]);
      })
      .finally(() => {
        setIsLoadingReceipts(false);
      });
  };

  const totalSize = useMemo(
    () => selectedFiles.reduce((acc, preview) => acc + preview.file.size, 0),
    [selectedFiles],
  );

  const filteredReceipts = useMemo(() => {
    if (!brandFilter) {
      return receipts;
    }
    return receipts.filter((receipt) => receipt.brand?.toLowerCase().includes(brandFilter.toLowerCase()));
  }, [brandFilter, receipts]);

  const receiptColumns = useMemo<TableColumn<ReceiptRecord>[]>(
    () => [
      { header: "Arquivo", accessor: "filename" },
      {
        header: "Marca",
        render: (receipt) => receipt.brand ?? "—",
      },
      {
        header: "Tamanho",
        render: (receipt) => formatSize(receipt.size_bytes),
      },
      {
        header: "Enviado em",
        render: (receipt) => (receipt.uploaded_at ? formatDate(receipt.uploaded_at) : "—"),
      },
      {
        header: "Ações",
        width: "160px",
        render: (receipt) => (
          <div className={styles.tableActions}>
            <Button size="sm" variant="secondary" type="button" onClick={() => startEdit(receipt)}>
              Editar
            </Button>
          </div>
        ),
      },
    ],
    [],
  );

  const handleFiles = (files: FileList | File[]) => {
    const next: PreviewFile[] = [];
    for (const file of Array.from(files)) {
      if (!file.type.startsWith("image")) {
        continue;
      }
      const duplicate = selectedFiles.some(
        (preview) => preview.file.name === file.name && preview.file.size === file.size,
      );
      if (duplicate) {
        continue;
      }
      next.push({ file, previewUrl: URL.createObjectURL(file) });
    }
    if (next.length === 0) {
      return;
    }
    setSelectedFiles((current) => [...current, ...next]);
    setUploadError(null);
    setUploadMessage(null);
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    if (event.dataTransfer.files?.length) {
      handleFiles(event.dataTransfer.files);
    }
  };

  const handleFileInput = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files?.length) {
      handleFiles(event.target.files);
      event.target.value = "";
    }
  };

  const removePreview = (previewUrl: string) => {
    setSelectedFiles((current) => {
      const filtered = current.filter((item) => item.previewUrl !== previewUrl);
      const removed = current.find((item) => item.previewUrl === previewUrl);
      if (removed) {
        URL.revokeObjectURL(removed.previewUrl);
      }
      return filtered;
    });
  };

  const goToStep = (nextStep: UploadStep) => {
    setStep(nextStep);
    setUploadError(null);
    setUploadMessage(null);
  };

  const handleUpload = async () => {
    setIsUploading(true);
    setUploadError(null);
    setUploadMessage(null);
    try {
      await uploadReceipts({
        files: selectedFiles.map((item) => item.file),
        brandId: selectedBrand ? Number(selectedBrand) : undefined,
      });
      setUploadMessage("Upload concluído com sucesso.");
      selectedFiles.forEach((preview) => URL.revokeObjectURL(preview.previewUrl));
      setSelectedFiles([]);
      setSelectedBrand("");
      setStep(4);
      loadReceipts();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Não foi possível enviar os arquivos.";
      setUploadError(message);
    } finally {
      setIsUploading(false);
    }
  };

  const startEdit = (receipt: ReceiptRecord) => {
    setEditReceipt(receipt);
    setEditForm({
      filename: receipt.filename,
      brand_id: receipt.brand_id ? String(receipt.brand_id) : "",
    });
    setEditErrors({});
  };

  const closeEdit = () => {
    setEditReceipt(null);
    setEditForm({ filename: "", brand_id: "" });
    setEditErrors({});
    setIsSavingEdit(false);
  };

  const handleEditSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!editReceipt) {
      return;
    }
    if (!editForm.filename.trim()) {
      setEditErrors({ filename: "Informe um nome de arquivo." });
      return;
    }
    setIsSavingEdit(true);
    setEditErrors({});
    try {
      await updateReceipt(editReceipt.id, {
        filename: editForm.filename.trim(),
        brand_id: editForm.brand_id ? Number(editForm.brand_id) : null,
      });
      closeEdit();
      loadReceipts();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Não foi possível atualizar o comprovante.";
      setEditErrors({ global: message });
    } finally {
      setIsSavingEdit(false);
    }
  };

  return (
    <div className={styles.container}>
      <header className="page-header">
        <h1>Comprovantes</h1>
        <p>Faça upload e organize comprovantes de pagamento enviados pelos parceiros.</p>
      </header>

      <Card title="Importar comprovantes" subtitle="Selecione imagens dos comprovantes e vincule a uma marca, se necessário.">
        <div className={styles.stepper} aria-label="Progresso do upload">
          {[1, 2, 3, 4].map((value) => (
            <div key={value} className={styles.step} data-active={step === value}>
              <span className={styles.stepNumber}>{value}</span>
              <span className={styles.stepLabel}>
                {value === 1 && "Selecionar"}
                {value === 2 && "Revisar"}
                {value === 3 && "Importar"}
                {value === 4 && "Concluído"}
              </span>
            </div>
          ))}
        </div>

        {step === 1 ? (
          <section className={styles.stepContent}>
            <div
              className={styles.dropArea}
              onDragOver={(event) => event.preventDefault()}
              onDragEnter={(event) => event.preventDefault()}
              onDrop={handleDrop}
            >
              <p>
                Arraste e solte imagens aqui ou
                <button type="button" className={styles.browseButton} onClick={() => document.getElementById("file-input")?.click()}>
                  escolher arquivos
                </button>
              </p>
              <input id="file-input" type="file" accept="image/*" multiple className={styles.hiddenInput} onChange={handleFileInput} />
            </div>

            <FormField label="Marca associada" htmlFor="upload-brand">
              <SelectInput
                id="upload-brand"
                value={selectedBrand}
                onChange={(event) => setSelectedBrand(event.target.value)}
              >
                <option value="">Sem marca</option>
                {brands.map((brand) => (
                  <option key={brand.id} value={brand.id}>
                    {brand.marca}
                  </option>
                ))}
              </SelectInput>
            </FormField>

            {selectedFiles.length > 0 ? (
              <ul className={styles.previewList}>
                {selectedFiles.map((preview) => (
                  <li key={preview.previewUrl} className={styles.previewItem}>
                    <img src={preview.previewUrl} alt={`Pré-visualização de ${preview.file.name}`} />
                    <div>
                      <strong>{preview.file.name}</strong>
                      <span>{formatSize(preview.file.size)}</span>
                    </div>
                    <button type="button" onClick={() => removePreview(preview.previewUrl)} aria-label={`Remover ${preview.file.name}`}>
                      ×
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <p className={styles.helperText}>Nenhum arquivo selecionado.</p>
            )}

            <div className={styles.stepActions}>
              <Button type="button" onClick={() => goToStep(2)} disabled={selectedFiles.length === 0}>
                Continuar
              </Button>
            </div>
          </section>
        ) : null}

        {step === 2 ? (
          <section className={styles.stepContent}>
            <h2>Pré-visualização</h2>
            <p>
              {selectedFiles.length} arquivo(s) selecionado(s) · Tamanho total {formatSize(totalSize)} · Marca:
              {" "}
              {selectedBrand
                ? brands.find((brand) => String(brand.id) === selectedBrand)?.marca ?? "N/D"
                : "Não associada"}
            </p>
            <div className={styles.previewGrid}>
              {selectedFiles.map((preview) => (
                <figure key={preview.previewUrl}>
                  <img src={preview.previewUrl} alt={`Pré-visualização de ${preview.file.name}`} />
                  <figcaption>{preview.file.name}</figcaption>
                </figure>
              ))}
            </div>
            <div className={styles.stepActions}>
              <Button type="button" variant="secondary" onClick={() => goToStep(1)}>
                Voltar
              </Button>
              <Button type="button" onClick={() => goToStep(3)}>
                Prosseguir para importação
              </Button>
            </div>
          </section>
        ) : null}

        {step === 3 ? (
          <section className={styles.stepContent}>
            <h2>Importação</h2>
            <p>Confirme o envio dos comprovantes selecionados. Você poderá editar os metadados após o upload.</p>
            {uploadError ? <div className={styles.errorMessage}>{uploadError}</div> : null}
            <div className={styles.stepActions}>
              <Button type="button" variant="secondary" onClick={() => goToStep(2)} disabled={isUploading}>
                Voltar
              </Button>
              <Button type="button" onClick={handleUpload} disabled={isUploading}>
                {isUploading ? "Enviando..." : "Iniciar importação"}
              </Button>
            </div>
          </section>
        ) : null}

        {step === 4 ? (
          <section className={styles.stepContent}>
            <h2>Upload concluído</h2>
            {uploadMessage ? (
              <div className={styles.successMessage} role="status" aria-live="polite">
                {uploadMessage}
              </div>
            ) : null}
            <p>Os comprovantes foram adicionados à sua biblioteca. Você pode editar informações individuais abaixo.</p>
            <div className={styles.stepActions}>
              <Button type="button" onClick={() => goToStep(1)}>
                Importar novos arquivos
              </Button>
            </div>
          </section>
        ) : null}
      </Card>

      <Card title="Comprovantes enviados" subtitle="Visualize e atualize os arquivos já importados.">
        <div className={styles.toolbar}>
          <FormField label="Filtrar por marca" htmlFor="filter-brand">
            <TextInput
              id="filter-brand"
              value={brandFilter}
              onChange={(event) => setBrandFilter(event.target.value)}
              placeholder="Digite o nome da marca"
            />
          </FormField>
          <Button type="button" variant="ghost" onClick={loadReceipts}>
            Recarregar lista
          </Button>
        </div>

        {receiptsError ? <div className={styles.errorMessage}>{receiptsError}</div> : null}
        {isLoadingReceipts ? <div className={styles.loadingMessage}>Carregando comprovantes...</div> : null}
        {!isLoadingReceipts && filteredReceipts.length === 0 && !receiptsError ? (
          <div className={styles.emptyState}>Nenhum comprovante cadastrado.</div>
        ) : null}
        {!isLoadingReceipts && filteredReceipts.length > 0 ? (
          <DataTable
            columns={receiptColumns}
            data={filteredReceipts}
            keyExtractor={(receipt) => receipt.id.toString()}
          />
        ) : null}
      </Card>

      <Modal
        isOpen={Boolean(editReceipt)}
        onClose={closeEdit}
        title={editReceipt ? `Editar ${editReceipt.filename}` : "Editar comprovante"}
        footer={
          <>
            <Button type="button" variant="ghost" onClick={closeEdit}>
              Cancelar
            </Button>
            <Button type="submit" form="receipt-edit-form" disabled={isSavingEdit}>
              {isSavingEdit ? "Salvando..." : "Salvar alterações"}
            </Button>
          </>
        }
      >
        <form id="receipt-edit-form" className={styles.form} onSubmit={handleEditSubmit}>
          {editErrors.global ? <div className={styles.errorMessage}>{editErrors.global}</div> : null}
          <FormField label="Nome do arquivo" htmlFor="edit-filename" error={editErrors.filename}>
            <TextInput
              id="edit-filename"
              value={editForm.filename}
              onChange={(event) => setEditForm((current) => ({ ...current, filename: event.target.value }))}
              hasError={Boolean(editErrors.filename)}
              required
            />
          </FormField>
          <FormField label="Marca associada" htmlFor="edit-brand">
            <SelectInput
              id="edit-brand"
              value={editForm.brand_id}
              onChange={(event) => setEditForm((current) => ({ ...current, brand_id: event.target.value }))}
            >
              <option value="">Sem marca</option>
              {brands.map((brand) => (
                <option key={brand.id} value={brand.id}>
                  {brand.marca}
                </option>
              ))}
            </SelectInput>
          </FormField>
        </form>
      </Modal>
    </div>
  );
}
