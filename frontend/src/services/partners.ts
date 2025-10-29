import httpClient from "@/services/httpClient";

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

type ListPartnersResponse = {
  data: PartnerRecord[];
};

type PartnerResponse = {
  data: PartnerRecord;
};

type DeletePartnerResponse = {
  data: {
    ok: boolean;
  };
};

export async function listPartners() {
  const response = await httpClient.get<ListPartnersResponse>("/api/partners");
  return response.data;
}

export async function createPartner(payload: PartnerPayload) {
  const response = await httpClient.post<PartnerResponse>("/api/partners", payload);
  return response.data;
}

export async function updatePartner(id: number, payload: Partial<PartnerPayload>) {
  const response = await httpClient.put<PartnerResponse>(`/api/partners/${id}`, payload);
  return response.data;
}

export async function deletePartner(id: number) {
  const response = await httpClient.delete<DeletePartnerResponse>(`/api/partners/${id}`);
  return response.data;
}
