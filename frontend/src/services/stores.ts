import httpClient from "@/services/httpClient";

type StoreRecord = {
  id: number;
  marca_id: number;
  marca: string;
  loja: string;
  cod_disagua: string | null;
  local_entrega: string;
  endereco: string | null;
  municipio: string;
  uf: string;
  valor_20l: number;
  valor_10l: number;
  valor_1500ml: number;
  valor_cx_copo: number;
  valor_vasilhame: number;
};

type StoresResponse = {
  data: StoreRecord[];
};

export async function listStores() {
  const response = await httpClient.get<StoresResponse>("/api/stores");
  return response.data;
}

export type { StoreRecord };
