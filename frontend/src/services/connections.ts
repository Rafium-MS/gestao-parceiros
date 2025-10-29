import httpClient, { unwrapData, type ApiData } from "@/services/httpClient";

export type ConnectionRecord = {
  id: number;
  partner_id: number;
  store_id: number;
};

export async function listConnections() {
  const response = await httpClient.get<ApiData<ConnectionRecord[]> | ConnectionRecord[] | null>(
    "/api/connections",
  );
  const data = unwrapData<ConnectionRecord[]>(response);
  if (!Array.isArray(data)) {
    throw new Error("Resposta inválida ao listar conexões.");
  }
  return data;
}

export async function createConnection(partnerId: number, storeId: number) {
  const response = await httpClient.post<ApiData<{ id?: number; ok?: boolean }> | { id?: number; ok?: boolean } | null>(
    "/api/connections",
    {
      partner_id: partnerId,
      store_id: storeId,
    },
  );
  const data = unwrapData<{ id?: number; ok?: boolean }>(response);
  if (!data || typeof data !== "object") {
    throw new Error("Resposta inválida ao criar conexão.");
  }
  return data;
}

export async function deleteConnection(id: number) {
  const response = await httpClient.delete<ApiData<{ ok?: boolean }> | { ok?: boolean } | null>(
    `/api/connections/${id}`,
  );
  const data = unwrapData<{ ok?: boolean }>(response);
  if (!data || typeof data !== "object") {
    throw new Error("Resposta inválida ao remover conexão.");
  }
  return data;
}
