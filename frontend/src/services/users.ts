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

export async function listUsers() {
  const response = await httpClient.get<UsersResponse>("/api/users");
  return response.data;
}

export type { UserRecord };
