import httpClient, { unwrapData, type ApiData } from "@/services/httpClient";

export async function fetchStatus(): Promise<string> {
  try {
    const response = await httpClient.get<ApiData<{ id: number; username: string }> | { id: number; username: string } | null>(
      "/api/me",
    );
    const data = unwrapData<{ id: number; username: string }>(response);
    if (!data || typeof data !== "object" || typeof data.username !== "string") {
      throw new Error("Resposta inválida ao verificar status.");
    }
    return `Autenticado como ${data.username}.`;
  } catch (error) {
    return "API disponível, faça login para continuar.";
  }
}
