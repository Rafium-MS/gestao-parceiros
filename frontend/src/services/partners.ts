import httpClient, { unwrapData, type ApiData } from "@/services/httpClient";

export type PartnerRecord = {
  id: number;
  cidade: string;
  estado: string;
  parceiro: string;
  distribuidora: string | null;
  cnpj_cpf: string;
  telefone: string;
  email: string | null;
  dia_pagamento: number | null;
  banco: string | null;
  agencia_conta: string | null;
  pix: string | null;
  cx_copo: number;
  dez_litros: number;
  vinte_litros: number;
  mil_quinhentos_ml: number;
  vasilhame: number;
  total: number;
  created_at: string | null;
};

export type PartnerPayload = {
  cidade: string;
  estado: string;
  parceiro: string;
  cnpj_cpf: string;
  telefone: string;
  distribuidora?: string | null;
  email?: string | null;
  dia_pagamento?: number | null;
  banco?: string | null;
  agencia_conta?: string | null;
  pix?: string | null;
  cx_copo?: number;
  dez_litros?: number;
  vinte_litros?: number;
  mil_quinhentos_ml?: number;
  vasilhame?: number;
};

export type ImportErrorSummary = {
  row: number | null;
  message: string;
};

export type PartnerImportSummary = {
  total: number;
  created: number;
  updated: number;
  skipped: number;
  error_count: number;
  errors: ImportErrorSummary[];
};

export async function listPartners() {
  const response = await httpClient.get<ApiData<PartnerRecord[]> | PartnerRecord[] | null>("/api/partners");
  const data = unwrapData<PartnerRecord[]>(response);
  if (!Array.isArray(data)) {
    throw new Error("Resposta inválida ao listar parceiros.");
  }
  return data;
}

export async function createPartner(payload: PartnerPayload) {
  const response = await httpClient.post<ApiData<PartnerRecord> | PartnerRecord | null>("/api/partners", payload);
  const data = unwrapData<PartnerRecord>(response);
  if (!data || typeof data !== "object") {
    throw new Error("Resposta inválida ao criar parceiro.");
  }
  return data;
}

export async function updatePartner(id: number, payload: Partial<PartnerPayload>) {
  const response = await httpClient.put<ApiData<PartnerRecord> | PartnerRecord | null>(
    `/api/partners/${id}`,
    payload,
  );
  const data = unwrapData<PartnerRecord>(response);
  if (!data || typeof data !== "object") {
    throw new Error("Resposta inválida ao atualizar parceiro.");
  }
  return data;
}

export async function deletePartner(id: number) {
  const response = await httpClient.delete<ApiData<{ ok: boolean }> | { ok: boolean } | null>(
    `/api/partners/${id}`,
  );
  const data = unwrapData<{ ok: boolean }>(response);
  if (!data || typeof data !== "object" || typeof data.ok !== "boolean") {
    throw new Error("Resposta inválida ao excluir parceiro.");
  }
  return data;
}

export async function importPartners(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await httpClient.post<ApiData<PartnerImportSummary> | PartnerImportSummary | null>(
    "/api/partners/import",
    formData,
  );

  const data = unwrapData<PartnerImportSummary>(response);
  if (!data || typeof data !== "object") {
    throw new Error("Resposta inválida ao importar parceiros.");
  }

  return data;
}
