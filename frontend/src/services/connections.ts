import httpClient from "@/services/httpClient";

export type ConnectionRecord = {
  id: number;
  partner_id: number;
  store_id: number;
};

type ConnectionListResponse = {
  data: ConnectionRecord[];
};

type MutationResponse = {
  data: {
    id?: number;
    ok?: boolean;
  };
};

export async function listConnections() {
  const response = await httpClient.get<ConnectionListResponse>("/api/connections");
  return response.data;
}

export async function createConnection(partnerId: number, storeId: number) {
  const response = await httpClient.post<MutationResponse>("/api/connections", {
    partner_id: partnerId,
    store_id: storeId,
  });
  return response.data;
}

export async function deleteConnection(id: number) {
  const response = await httpClient.delete<MutationResponse>(`/api/connections/${id}`);
  return response.data;
}
