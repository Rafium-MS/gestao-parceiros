import { ChangeEvent, DragEvent, FormEvent, useEffect, useMemo, useRef, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable, TableColumn } from "@/components/ui/DataTable";
import { FormField } from "@/components/ui/FormField";
import { Modal } from "@/components/ui/Modal";
import { SelectInput } from "@/components/ui/SelectInput";
import { TableSkeleton } from "@/components/ui/TableSkeleton";
import { TextInput } from "@/components/ui/TextInput";
import { listBrands, type BrandRecord } from "@/services/brands";
import { listReceipts, type ReceiptRecord, updateReceipt } from "@/services/receipts";
import { env } from "@/config/env";
import { formatDate } from "@/utils/formatters";
import { useToast } from "@/contexts/ToastContext";

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

type UploadStatus = {
  progress: number;
  status: "pending" | "uploading" | "success" | "error";
  error?: string;
};

function formatSize(size: number) {
  const megabytes = size / (1024 * 1024);
  if (megabytes >= 1) {
    return `${megabytes.toFixed(2)} MB`;
  }
  const kilobytes = size / 1024;
  return `${kilobytes.toFixed(1)} KB`;
}

function normalizeApiResponse<T>(payload: { data?: T } | T | null | undefined): T | null | undefined {
  if (payload && typeof payload === "object" && "data" in payload) {
    return (payload as { data?: T }).data;
  }
  return payload as T | null | undefined;
}

async function uploadReceiptWithProgress(
  file: File,
  brandId: number | undefined,
  onProgress: (value: number) => void,
) {
  return new Promise<{
    saved: Array<{ id: number; filename: string; size_bytes: number; brand_id: number | null }>;
  }>((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const baseUrl = env.apiBaseUrl.replace(/\/$/, "");
    xhr.open("POST", `${baseUrl}/api/upload`);
    xhr.responseType = "json";
    xhr.withCredentials = true;
    xhr.setRequestHeader("Accept", "application/json");

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        const progress = Math.round((event.loaded / event.total) * 100);
        onProgress(progress);
      }
    };

    xhr.onerror = () => {
      reject(new Error("Não foi possível enviar o arquivo."));
    };

    xhr.onload = () => {
      const status = xhr.status;
      const responseBody = xhr.response ?? xhr.responseText;

      if (status < 200 || status >= 300) {
        let message = "Não foi possível enviar o arquivo.";
        if (responseBody && typeof responseBody === "object" && "error" in responseBody) {
          const payload = responseBody as { error?: { message?: string } };
          message = payload.error?.message ?? message;
        } else if (typeof responseBody === "string") {
          try {
            const parsed = JSON.parse(responseBody);
            if (parsed && typeof parsed === "object" && "error" in parsed) {
              message = parsed.error?.message ?? message;
            }
          } catch {
            message = responseBody || message;
          }
        }
        reject(new Error(message));
        return;
      }

      try {
        const parsedResponse =
          typeof responseBody === "string" && responseBody ? JSON.parse(responseBody) : responseBody;
        const data = normalizeApiResponse(parsedResponse);
        if (!data || typeof data !== "object" || !Array.isArray((data as { saved?: unknown }).saved)) {
          throw new Error("Resposta inválida ao enviar comprovantes.");
        }
        onProgress(100);
        resolve(data as {
          saved: Array<{ id: number; filename: string; size_bytes: number; brand_id: number | null }>;
        });
      } catch (error) {
        reject(error instanceof Error ? error : new Error("Resposta inválida ao enviar comprovantes."));
      }
    };

    const formData = new FormData();
    formData.append("files", file);
    if (typeof brandId === "number") {
      formData.append("brand_id", brandId.toString());
    }

    xhr.send(formData);
  });
}

export function ReceiptsPage() {
  const [step, setStep] = useState<UploadStep>(1);
  const [brands, setBrands] = useState<BrandRecord[]>([]);
  const [brandFilter, setBrandFilter] = useState<string>("");
  const [selectedFiles, setSelectedFiles] = useState<PreviewFile[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<string>("");
  const [uploadProgress, setUploadProgress] = useState<Record<string, UploadStatus>>({});
  const [receipts, setReceipts] = useState<ReceiptRecord[]>([]);
  const [isLoadingReceipts, setIsLoadingReceipts] = useState(false);
  const [receiptsError, setReceiptsError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [editReceipt, setEditReceipt] = useState<ReceiptRecord | null>(null);
  const [editForm, setEditForm] = useState<EditFormState>({ filename: "", brand_id: "" });
  const [editErrors, setEditErrors] = useState<EditFormErrors>({});
  const [isSavingEdit, setIsSavingEdit] = useState(false);
  const [zoomPreview, setZoomPreview] = useState<PreviewFile | null>(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const dragDepthRef = useRef(0);
  const { showError, showSuccess } = useToast();

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
        showError(message);
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
    setUploadProgress((current) => {
      const updated = { ...current };
      next.forEach((preview) => {
        updated[preview.previewUrl] = { status: "pending", progress: 0 };
      });
      return updated;
    });
  };

  const handleDragEnter = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    dragDepthRef.current += 1;
    setIsDragActive(true);
  };

  const handleDragLeave = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    dragDepthRef.current = Math.max(0, dragDepthRef.current - 1);
    if (dragDepthRef.current === 0) {
      setIsDragActive(false);
    }
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    dragDepthRef.current = 0;
    setIsDragActive(false);
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
    setUploadProgress((current) => {
      const nextState = { ...current };
      delete nextState[previewUrl];
      return nextState;
    });
  };

  const goToStep = (nextStep: UploadStep) => {
    setStep(nextStep);
  };

  const updateUploadStatus = (previewUrl: string, partial: Partial<UploadStatus>) => {
    setUploadProgress((current) => {
      const previous = current[previewUrl] ?? { progress: 0, status: "pending" };
      return {
        ...current,
        [previewUrl]: {
          ...previous,
          ...partial,
        },
      };
    });
  };

  const handleUpload = async () => {
    setIsUploading(true);
    try {
      const successfulUploads: string[] = [];
      const failedUploads: string[] = [];
      const brandId = selectedBrand ? Number(selectedBrand) : undefined;

      for (const preview of selectedFiles) {
        updateUploadStatus(preview.previewUrl, { status: "uploading", progress: 0, error: undefined });
        try {
          await uploadReceiptWithProgress(preview.file, brandId, (progress) => {
            updateUploadStatus(preview.previewUrl, { progress });
          });
          successfulUploads.push(preview.previewUrl);
          updateUploadStatus(preview.previewUrl, { status: "success", progress: 100 });
        } catch (error) {
          const message = error instanceof Error ? error.message : "Não foi possível enviar o arquivo.";
          failedUploads.push(preview.previewUrl);
          updateUploadStatus(preview.previewUrl, { status: "error", error: message });
        }
      }

      const hasSuccess = successfulUploads.length > 0;
      const hasFailure = failedUploads.length > 0;

      if (hasSuccess) {
        const message = hasFailure
          ? `${successfulUploads.length} arquivo(s) enviado(s) com sucesso.`
          : "Upload concluído com sucesso.";
        showSuccess(message);
        loadReceipts();
      }

      if (hasFailure) {
        const message = hasSuccess
          ? "Alguns arquivos não puderam ser enviados. Verifique os detalhes abaixo."
          : "Não foi possível enviar os arquivos selecionados.";
        showError(message);
      }

      if (!hasFailure && hasSuccess) {
        setSelectedFiles([]);
        setSelectedBrand("");
        setUploadProgress({});
        setStep(4);
      } else if (hasSuccess && hasFailure) {
        const failedSet = new Set(failedUploads);
        setSelectedFiles((current) => {
          current.forEach((preview) => {
            if (!failedSet.has(preview.previewUrl)) {
              URL.revokeObjectURL(preview.previewUrl);
            }
          });
          return current.filter((preview) => failedSet.has(preview.previewUrl));
        });
        setUploadProgress((current) => {
          const nextState: Record<string, UploadStatus> = {};
          failedUploads.forEach((previewUrl) => {
            if (current[previewUrl]) {
              nextState[previewUrl] = current[previewUrl];
            }
          });
          return nextState;
        });
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Não foi possível enviar os arquivos.";
      showError(message);
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
      showSuccess("Comprovante atualizado com sucesso.");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Não foi possível atualizar o comprovante.";
      setEditErrors({ global: message });
      showError(message);
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

            <p className={styles.brandHint}>
              A marca selecionada será aplicada a todos os comprovantes enviados neste lote.
            </p>

            <div
              className={styles.dropArea}
              data-active={isDragActive}
              onDragOver={(event) => event.preventDefault()}
              onDragEnter={handleDragEnter}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <div className={styles.dropIcon} aria-hidden>
                ⬆
              </div>
              <p>
                Arraste e solte imagens aqui ou
                <button type="button" className={styles.browseButton} onClick={() => document.getElementById("file-input")?.click()}>
                  escolher arquivos
                </button>
              </p>
              <span className={styles.dropHint}>Formatos suportados: JPG, PNG, GIF e WEBP.</span>
              <input id="file-input" type="file" accept="image/*" multiple className={styles.hiddenInput} onChange={handleFileInput} />
            </div>

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
            <p className={styles.previewHint}>Clique em uma imagem para visualizar em tela cheia.</p>
            <div className={styles.previewGrid}>
              {selectedFiles.map((preview) => (
                <figure key={preview.previewUrl} className={styles.previewFigure}>
                  <button
                    type="button"
                    className={styles.previewZoomButton}
                    onClick={() => setZoomPreview(preview)}
                    aria-label={`Ampliar ${preview.file.name}`}
                  >
                    <img src={preview.previewUrl} alt={`Pré-visualização de ${preview.file.name}`} />
                  </button>
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
            <ul className={styles.progressList}>
              {selectedFiles.map((preview) => {
                const status = uploadProgress[preview.previewUrl] ?? { status: "pending", progress: 0 };
                return (
                  <li key={preview.previewUrl} className={styles.progressItem} data-status={status.status}>
                    <div className={styles.progressInfo}>
                      <span className={styles.progressName}>{preview.file.name}</span>
                      <span className={styles.progressStatus}>
                        {status.status === "success"
                          ? "Concluído"
                          : status.status === "error"
                          ? "Falhou"
                          : `${status.progress}%`}
                      </span>
                    </div>
                    <div
                      className={styles.progressBar}
                      role="progressbar"
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-valuenow={Math.min(100, Math.max(0, status.progress))}
                    >
                      <div
                        className={styles.progressFill}
                        style={{ width: `${Math.min(100, Math.max(0, status.progress))}%` }}
                      />
                    </div>
                    {status.status === "error" && status.error ? (
                      <p className={styles.progressError}>{status.error}</p>
                    ) : null}
                  </li>
                );
              })}
            </ul>
            <div className={styles.stepActions}>
              <Button type="button" variant="secondary" onClick={() => goToStep(2)} disabled={isUploading}>
                Voltar
              </Button>
              <Button type="button" onClick={handleUpload} isLoading={isUploading} loadingText="Enviando...">
                Iniciar importação
              </Button>
            </div>
          </section>
        ) : null}

        {step === 4 ? (
          <section className={styles.stepContent}>
            <h2>Upload concluído</h2>
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

        {isLoadingReceipts ? <TableSkeleton columns={receiptColumns.length} /> : null}
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
            <Button
              type="submit"
              form="receipt-edit-form"
              isLoading={isSavingEdit}
              loadingText="Salvando..."
            >
              Salvar alterações
            </Button>
          </>
        }
      >
        <form id="receipt-edit-form" className={styles.form} onSubmit={handleEditSubmit}>
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
      <Modal
        isOpen={Boolean(zoomPreview)}
        onClose={() => setZoomPreview(null)}
        title={zoomPreview ? zoomPreview.file.name : "Pré-visualização"}
      >
        {zoomPreview ? (
          <div className={styles.zoomContent}>
            <img src={zoomPreview.previewUrl} alt={`Versão ampliada de ${zoomPreview.file.name}`} />
          </div>
        ) : null}
      </Modal>
    </div>
  );
}
