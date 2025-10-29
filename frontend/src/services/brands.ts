import httpClient from "@/services/httpClient";

type BrandRecord = {
  id: number;
  marca: string;
  cod_disagua: string | null;
  store_count: number;
};

type BrandsResponse = {
  data: BrandRecord[];
};

type BrandPayload = {
  marca: string;
  cod_disagua?: string | null;
};

type BrandResponse = {
  data: BrandRecord;
};

type DeleteBrandResponse = {
  data: {
    ok: boolean;
  };
};

export async function listBrands() {
  const response = await httpClient.get<BrandsResponse>("/api/brands");
  return response.data;
}

export async function createBrand(payload: BrandPayload) {
  const response = await httpClient.post<BrandResponse>("/api/brands", payload);
  return response.data;
}

export async function updateBrand(id: number, payload: Partial<BrandPayload>) {
  const response = await httpClient.put<BrandResponse>(`/api/brands/${id}`, payload);
  return response.data;
}

export async function deleteBrand(id: number) {
  const response = await httpClient.delete<DeleteBrandResponse>(`/api/brands/${id}`);
  return response.data;
}

export type { BrandRecord, BrandPayload };
