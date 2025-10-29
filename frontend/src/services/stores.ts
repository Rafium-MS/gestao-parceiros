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

type StorePayload = {
  marca_id: number;
  loja?: string;
  cod_disagua?: string | null;
  local_entrega?: string;
  endereco?: string | null;
  municipio?: string;
  uf?: string;
  valor_20l?: number;
  valor_10l?: number;
  valor_1500ml?: number;
  valor_cx_copo?: number;
  valor_vasilhame?: number;
};

type StoreResponse = {
  data: StoreRecord;
};

type DeleteStoreResponse = {
  data: {
    ok: boolean;
  };
};

export async function listStores() {
  const response = await httpClient.get<StoresResponse>("/api/stores");
  return response.data;
}

export async function createStore(payload: StorePayload) {
  const response = await httpClient.post<StoreResponse>("/api/stores", payload);
  return response.data;
}

export async function updateStore(id: number, payload: Partial<StorePayload>) {
  const response = await httpClient.put<StoreResponse>(`/api/stores/${id}`, payload);
  return response.data;
}

export async function deleteStore(id: number) {
  const response = await httpClient.delete<DeleteStoreResponse>(`/api/stores/${id}`);
  return response.data;
}

export type { StoreRecord, StorePayload };
