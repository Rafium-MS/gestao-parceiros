import httpClient, { unwrapData, type ApiData } from "@/services/httpClient";

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

export async function listStores() {
  const response = await httpClient.get<ApiData<StoreRecord[]> | StoreRecord[] | null>("/api/stores");
  const data = unwrapData<StoreRecord[]>(response);
  if (!Array.isArray(data)) {
    throw new Error("Resposta inválida ao listar lojas.");
  }
  return data;
}

export async function createStore(payload: StorePayload) {
  const response = await httpClient.post<ApiData<StoreRecord> | StoreRecord | null>("/api/stores", payload);
  const data = unwrapData<StoreRecord>(response);
  if (!data || typeof data !== "object") {
    throw new Error("Resposta inválida ao criar loja.");
  }
  return data;
}

export async function updateStore(id: number, payload: Partial<StorePayload>) {
  const response = await httpClient.put<ApiData<StoreRecord> | StoreRecord | null>(
    `/api/stores/${id}`,
    payload,
  );
  const data = unwrapData<StoreRecord>(response);
  if (!data || typeof data !== "object") {
    throw new Error("Resposta inválida ao atualizar loja.");
  }
  return data;
}

export async function deleteStore(id: number) {
  const response = await httpClient.delete<ApiData<{ ok: boolean }> | { ok: boolean } | null>(
    `/api/stores/${id}`,
  );
  const data = unwrapData<{ ok: boolean }>(response);
  if (!data || typeof data !== "object" || typeof data.ok !== "boolean") {
    throw new Error("Resposta inválida ao excluir loja.");
  }
  return data;
}

export type { StoreRecord, StorePayload };
