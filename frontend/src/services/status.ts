import httpClient from "@/services/httpClient";

type ApiStatusResponse = {
  data: {
    id: number;
    username: string;
  };
};

export async function fetchStatus(): Promise<string> {
  try {
    const response = await httpClient.get<ApiStatusResponse>("/api/me");
    return `Autenticado como ${response.data.username}.`;
  } catch (error) {
    return "API disponível, faça login para continuar.";
  }
}
