import httpClient, { unwrapData, type ApiData } from "@/services/httpClient";

export type AuthenticatedUser = {
  id: number;
  username: string;
  role: string;
};

export async function login(username: string, password: string) {
  const response = await httpClient.post<
    ApiData<{ user: AuthenticatedUser }> | { user: AuthenticatedUser } | null
  >("/api/login", { username, password });
  const data = unwrapData<{ user: AuthenticatedUser }>(response);
  if (!data || typeof data !== "object" || !data.user) {
    throw new Error("Resposta inválida ao autenticar usuário.");
  }
  return data.user;
}

export async function logout() {
  await httpClient.post("/api/logout");
}

export async function fetchCurrentUser() {
  const response = await httpClient.get<ApiData<AuthenticatedUser> | AuthenticatedUser | null>("/api/me");
  const data = unwrapData<AuthenticatedUser>(response);
  if (!data || typeof data !== "object") {
    throw new Error("Resposta inválida ao carregar usuário atual.");
  }
  return data;
}
