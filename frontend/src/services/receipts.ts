import httpClient, { unwrapData, type ApiData } from "@/services/httpClient";

export type ReceiptRecord = {
  id: number;
  filename: string;
  brand_id: number | null;
  brand: string | null;
  size_bytes: number;
  uploaded_at: string | null;
  url: string;
};

export type UploadReceiptPayload = {
  files: File[];
  brandId?: number | null;
};

type UpdateReceiptPayload = {
  filename?: string;
  brand_id?: number | null;
};

export async function listReceipts() {
  const response = await httpClient.get<ApiData<ReceiptRecord[]> | ReceiptRecord[] | null>(
    "/api/receipts",
  );
  const data = unwrapData<ReceiptRecord[]>(response);
  if (!Array.isArray(data)) {
    throw new Error("Resposta inválida ao listar comprovantes.");
  }
  return data;
}

export async function uploadReceipts({ files, brandId }: UploadReceiptPayload) {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  if (typeof brandId === "number") {
    formData.append("brand_id", brandId.toString());
  }

  const response = await httpClient.post<
    ApiData<{ saved: Array<{ id: number; filename: string; size_bytes: number; brand_id: number | null }> }> |
      { saved: Array<{ id: number; filename: string; size_bytes: number; brand_id: number | null }> } |
      null
  >("/api/upload", formData, {
    headers: {
      Accept: "application/json",
    },
  });
  const data = unwrapData<{ saved: Array<{ id: number; filename: string; size_bytes: number; brand_id: number | null }> }>(
    response,
  );
  if (!data || typeof data !== "object" || !Array.isArray(data.saved)) {
    throw new Error("Resposta inválida ao enviar comprovantes.");
  }
  return data;
}

export async function updateReceipt(id: number, payload: UpdateReceiptPayload) {
  const response = await httpClient.put<ApiData<{ ok: boolean }> | { ok: boolean } | null>(
    `/api/receipts/${id}`,
    payload,
  );
  const data = unwrapData<{ ok: boolean }>(response);
  if (!data || typeof data !== "object" || typeof data.ok !== "boolean") {
    throw new Error("Resposta inválida ao atualizar comprovante.");
  }
  return data;
}
