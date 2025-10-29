import httpClient, { unwrapData, type ApiData } from "@/services/httpClient";

type UserRecord = {
  id: number;
  username: string;
  role: string;
  is_active: boolean;
};

type CreateUserPayload = {
  username: string;
  password: string;
  role: string;
  is_active: boolean;
};

type UpdateUserPayload = Partial<Pick<CreateUserPayload, "role" | "is_active" >>;

export async function listUsers() {
  const response = await httpClient.get<ApiData<UserRecord[]> | UserRecord[] | null>("/api/users");
  const data = unwrapData<UserRecord[]>(response);
  if (!Array.isArray(data)) {
    throw new Error("Resposta inválida ao listar usuários.");
  }
  return data;
}

export async function createUser(payload: CreateUserPayload) {
  const response = await httpClient.post<ApiData<UserRecord> | UserRecord | null>("/api/users", payload);
  const data = unwrapData<UserRecord>(response);
  if (!data || typeof data !== "object") {
    throw new Error("Resposta inválida ao criar usuário.");
  }
  return data;
}

export async function updateUser(id: number, payload: UpdateUserPayload) {
  const response = await httpClient.put<ApiData<{ ok: boolean }> | { ok: boolean } | null>(
    `/api/users/${id}`,
    payload,
  );
  const data = unwrapData<{ ok: boolean }>(response);
  if (!data || typeof data !== "object" || typeof data.ok !== "boolean") {
    throw new Error("Resposta inválida ao atualizar usuário.");
  }
  return data;
}

export async function updateUserPassword(id: number, newPassword: string) {
  const response = await httpClient.put<ApiData<{ ok: boolean }> | { ok: boolean } | null>(
    `/api/users/${id}/password`,
    {
      new_password: newPassword,
    },
  );
  const data = unwrapData<{ ok: boolean }>(response);
  if (!data || typeof data !== "object" || typeof data.ok !== "boolean") {
    throw new Error("Resposta inválida ao atualizar senha do usuário.");
  }
  return data;
}

export async function deleteUser(id: number) {
  const response = await httpClient.delete<ApiData<{ ok: boolean }> | { ok: boolean } | null>(
    `/api/users/${id}`,
  );
  const data = unwrapData<{ ok: boolean }>(response);
  if (!data || typeof data !== "object" || typeof data.ok !== "boolean") {
    throw new Error("Resposta inválida ao remover usuário.");
  }
  return data;
}

export type { UserRecord, CreateUserPayload, UpdateUserPayload };
