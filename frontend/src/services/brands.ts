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

export async function listBrands() {
  const response = await httpClient.get<BrandsResponse>("/api/brands");
  return response.data;
}

export type { BrandRecord };
