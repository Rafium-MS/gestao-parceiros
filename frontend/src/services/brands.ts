import httpClient, { unwrapData, type ApiData } from "@/services/httpClient";
import { type ImportErrorSummary } from "@/services/partners";

type BrandRecord = {
  id: number;
  marca: string;
  cod_disagua: string | null;
  store_count: number;
};

type BrandPayload = {
  marca: string;
  cod_disagua?: string | null;
};

export type BrandStoreImportSummary = {
  total: number;
  created_brands: number;
  updated_brands: number;
  created_stores: number;
  updated_stores: number;
  skipped: number;
  error_count: number;
  errors: ImportErrorSummary[];
};

export async function listBrands() {
  const response = await httpClient.get<ApiData<BrandRecord[]> | BrandRecord[] | null>("/api/brands");
  const data = unwrapData<BrandRecord[]>(response);
  if (!Array.isArray(data)) {
    throw new Error("Resposta inválida ao listar marcas.");
  }
  return data;
}

export async function createBrand(payload: BrandPayload) {
  const response = await httpClient.post<ApiData<BrandRecord> | BrandRecord | null>("/api/brands", payload);
  const data = unwrapData<BrandRecord>(response);
  if (!data || typeof data !== "object") {
    throw new Error("Resposta inválida ao criar marca.");
  }
  return data;
}

export async function updateBrand(id: number, payload: Partial<BrandPayload>) {
  const response = await httpClient.put<ApiData<BrandRecord> | BrandRecord | null>(
    `/api/brands/${id}`,
    payload,
  );
  const data = unwrapData<BrandRecord>(response);
  if (!data || typeof data !== "object") {
    throw new Error("Resposta inválida ao atualizar marca.");
  }
  return data;
}

export async function deleteBrand(id: number) {
  const response = await httpClient.delete<ApiData<{ ok: boolean }> | { ok: boolean } | null>(
    `/api/brands/${id}`,
  );
  const data = unwrapData<{ ok: boolean }>(response);
  if (!data || typeof data !== "object" || typeof data.ok !== "boolean") {
    throw new Error("Resposta inválida ao excluir marca.");
  }
  return data;
}

export async function importBrandsAndStores(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await httpClient.post<
    ApiData<BrandStoreImportSummary> | BrandStoreImportSummary | null
  >("/api/brands/import", formData);

  const data = unwrapData<BrandStoreImportSummary>(response);
  if (!data || typeof data !== "object") {
    throw new Error("Resposta inválida ao importar marcas e lojas.");
  }

  return data;
}

export type { BrandRecord, BrandPayload };
