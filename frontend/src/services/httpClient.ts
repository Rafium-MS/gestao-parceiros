import { env } from "@/config/env";

type RequestBody = BodyInit | Record<string, unknown> | undefined;

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: RequestBody;
};

export type HttpErrorPayload = {
  error?: {
    message?: string;
    code?: string;
    [key: string]: unknown;
  };
  [key: string]: unknown;
};

export class HttpError extends Error {
  readonly status: number;
  readonly payload: HttpErrorPayload | string | null;

  constructor(message: string, status: number, payload: HttpErrorPayload | string | null) {
    super(message);
    this.name = "HttpError";
    this.status = status;
    this.payload = payload;
  }
}

const unauthorizedHandlers = new Set<() => void>();

export function onUnauthorized(handler: () => void) {
  unauthorizedHandlers.add(handler);
  return () => unauthorizedHandlers.delete(handler);
}

function buildUrl(path: string) {
  const baseUrl = env.apiBaseUrl.replace(/\/$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  if (!baseUrl) {
    return normalizedPath;
  }
  return `${baseUrl}${normalizedPath}`;
}

function prepareBody(body: RequestBody): BodyInit | undefined {
  if (!body) {
    return undefined;
  }

  if (body instanceof FormData || body instanceof URLSearchParams || body instanceof Blob) {
    return body;
  }

  if (typeof body === "string") {
    return body;
  }

  return JSON.stringify(body);
}

async function request<TResponse = unknown>(path: string, options: RequestOptions = {}) {
  const url = buildUrl(path);
  const headers = new Headers(options.headers);

  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  const preparedBody = prepareBody(options.body);

  if (preparedBody && !(preparedBody instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(url, {
    ...options,
    headers,
    body: preparedBody,
    credentials: "include",
  });

  const contentType = response.headers.get("content-type") ?? "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    const message =
      (payload && typeof payload === "object" && "error" in payload &&
        (payload as HttpErrorPayload).error?.message) ||
      (typeof payload === "string" && payload) ||
      "Falha ao comunicar com o servidor.";

    if (response.status === 401) {
      unauthorizedHandlers.forEach((handler) => handler());
    }

    throw new HttpError(message, response.status, isJson ? (payload as HttpErrorPayload) : payload);
  }

  return payload as TResponse;
}

export type ApiData<T> = { data: T };

export function unwrapData<T>(payload: ApiData<T> | T | null | undefined): T | null | undefined {
  if (payload && typeof payload === "object" && "data" in payload) {
    return (payload as ApiData<T>).data;
  }
  return payload as T | null | undefined;
}

export const httpClient = {
  request,
  get<TResponse = unknown>(path: string, options?: RequestOptions) {
    return request<TResponse>(path, { ...options, method: "GET" });
  },
  post<TResponse = unknown>(path: string, body?: RequestBody, options?: RequestOptions) {
    return request<TResponse>(path, { ...options, method: "POST", body });
  },
  put<TResponse = unknown>(path: string, body?: RequestBody, options?: RequestOptions) {
    return request<TResponse>(path, { ...options, method: "PUT", body });
  },
  delete<TResponse = unknown>(path: string, options?: RequestOptions) {
    return request<TResponse>(path, { ...options, method: "DELETE" });
  },
};

export default httpClient;
