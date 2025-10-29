import { env } from "@/config/env";

type ApiStatusResponse = {
  username?: string;
};

export async function fetchStatus(): Promise<string> {
  const response = await fetch(`${env.apiBaseUrl}/api/me`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Unable to reach API");
  }

  const data = (await response.json()) as ApiStatusResponse;
  if (data.username) {
    return `Autenticado como ${data.username}.`;
  }
  return "API disponível, faça login para continuar.";
}
