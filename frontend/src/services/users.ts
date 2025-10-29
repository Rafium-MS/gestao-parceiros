import httpClient from "@/services/httpClient";

type UserRecord = {
  id: number;
  username: string;
  role: string;
  is_active: boolean;
};

type UsersResponse = {
  data: UserRecord[];
};

type UserResponse = {
  data: UserRecord;
};

type MutationResponse = {
  data: {
    ok: boolean;
  };
};

type CreateUserPayload = {
  username: string;
  password: string;
  role: string;
  is_active: boolean;
};

type UpdateUserPayload = Partial<Pick<CreateUserPayload, "role" | "is_active" >>;

export async function listUsers() {
  const response = await httpClient.get<UsersResponse>("/api/users");
  return response.data;
}

export async function createUser(payload: CreateUserPayload) {
  const response = await httpClient.post<UserResponse>("/api/users", payload);
  return response.data;
}

export async function updateUser(id: number, payload: UpdateUserPayload) {
  const response = await httpClient.put<MutationResponse>(`/api/users/${id}`, payload);
  return response.data;
}

export async function updateUserPassword(id: number, newPassword: string) {
  const response = await httpClient.put<MutationResponse>(`/api/users/${id}/password`, {
    new_password: newPassword,
  });
  return response.data;
}

export async function deleteUser(id: number) {
  const response = await httpClient.delete<MutationResponse>(`/api/users/${id}`);
  return response.data;
}

export type { UserRecord, CreateUserPayload, UpdateUserPayload };
