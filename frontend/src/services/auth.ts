import httpClient from "@/services/httpClient";

export type AuthenticatedUser = {
  id: number;
  username: string;
  role: string;
};

type LoginResponse = {
  data: {
    user: AuthenticatedUser;
  };
};

type MeResponse = {
  data: AuthenticatedUser;
};

export async function login(username: string, password: string) {
  const response = await httpClient.post<LoginResponse>("/api/login", { username, password });
  return response.data.user;
}

export async function logout() {
  await httpClient.post("/api/logout");
}

export async function fetchCurrentUser() {
  const response = await httpClient.get<MeResponse>("/api/me");
  return response.data;
}
