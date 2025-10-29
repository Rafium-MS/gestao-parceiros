import httpClient from "@/services/httpClient";

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

type ReceiptListResponse = {
  data: ReceiptRecord[];
};

type UploadResponse = {
  data: {
    saved: Array<{
      id: number;
      filename: string;
      size_bytes: number;
      brand_id: number | null;
    }>;
  };
};

type UpdateReceiptPayload = {
  filename?: string;
  brand_id?: number | null;
};

type MutationResponse = {
  data: {
    ok: boolean;
  };
};

export async function listReceipts() {
  const response = await httpClient.get<ReceiptListResponse>("/api/receipts");
  return response.data;
}

export async function uploadReceipts({ files, brandId }: UploadReceiptPayload) {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  if (typeof brandId === "number") {
    formData.append("brand_id", brandId.toString());
  }

  const response = await httpClient.post<UploadResponse>("/api/upload", formData, {
    headers: {
      Accept: "application/json",
    },
  });
  return response.data;
}

export async function updateReceipt(id: number, payload: UpdateReceiptPayload) {
  const response = await httpClient.put<MutationResponse>(`/api/receipts/${id}`, payload);
  return response.data;
}
