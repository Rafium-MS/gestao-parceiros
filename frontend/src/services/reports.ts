import httpClient, { unwrapData, type ApiData } from "@/services/httpClient";

type ReportEntry = {
  id: number;
  marca: string;
  loja: string;
  data: string;
  valor_20l: number;
  valor_10l: number;
  valor_1500ml: number;
  valor_cx_copo: number;
  valor_vasilhame: number;
};

export type ReportDataFilters = {
  startDate?: string;
  endDate?: string;
  marca?: string;
};

export async function listReportEntries(filters: ReportDataFilters = {}) {
  const params = new URLSearchParams();
  if (filters.startDate) {
    params.set("startDate", filters.startDate);
  }
  if (filters.endDate) {
    params.set("endDate", filters.endDate);
  }
  if (filters.marca) {
    params.set("marca", filters.marca);
  }

  const query = params.toString();
  const response = await httpClient.get<ApiData<ReportEntry[]> | ReportEntry[] | null>(
    `/api/report-data${query ? `?${query}` : ""}`,
  );
  const data = unwrapData<ReportEntry[]>(response);
  if (!Array.isArray(data)) {
    throw new Error("Resposta inválida ao listar dados do relatório.");
  }
  return data;
}

export type { ReportEntry };
