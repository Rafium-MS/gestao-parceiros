import { useCallback } from "react";

import { env } from "@/config/env";

type ApiRequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
  baseUrl?: string;
  parseJson?: boolean;
};

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

type RequestFunction = <TResponse>(path: string, options?: ApiRequestOptions) => Promise<TResponse>;

type UseApiReturn = {
  request: RequestFunction;
  get: RequestFunction;
  post: RequestFunction;
  put: RequestFunction;
  patch: RequestFunction;
  del: RequestFunction;
};

export function useApi(defaultBaseUrl = env.apiBaseUrl): UseApiReturn {
  const request = useCallback<RequestFunction>(
    async (path, options = {}) => {
      const { body, baseUrl = defaultBaseUrl, parseJson = true, headers, ...rest } = options;
      const method = (rest.method ?? "GET").toUpperCase() as HttpMethod;
      const url = new URL(path, baseUrl).toString();

      let serializedBody: BodyInit | undefined;
      const resolvedHeaders = new Headers(headers);

      if (body instanceof FormData || body instanceof Blob) {
        serializedBody = body as BodyInit;
      } else if (body !== undefined) {
        serializedBody = JSON.stringify(body);
        if (!resolvedHeaders.has("Content-Type")) {
          resolvedHeaders.set("Content-Type", "application/json");
        }
      }

      const response = await fetch(url, {
        ...rest,
        method,
        headers: resolvedHeaders,
        body: serializedBody,
      });

      if (!response.ok) {
        const errorBody = await safeParseJson(response);
        throw new ApiError(response.status, response.statusText, errorBody);
      }

      if (!parseJson || method === "DELETE" || response.status === 204) {
        return undefined as TResponse;
      }

      return (await response.json()) as TResponse;
    },
    [defaultBaseUrl],
  );

  const withMethod = useCallback(
    (method: HttpMethod): RequestFunction =>
      (path, options = {}) =>
        request(path, {
          ...options,
          method,
        }),
    [request],
  );

  return {
    request,
    get: withMethod("GET"),
    post: withMethod("POST"),
    put: withMethod("PUT"),
    patch: withMethod("PATCH"),
    del: withMethod("DELETE"),
  };
}

export class ApiError extends Error {
  public readonly status: number;
  public readonly data: unknown;

  constructor(status: number, statusText: string, data: unknown) {
    super(`Erro ${status}: ${statusText}`);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

async function safeParseJson(response: Response) {
  const contentType = response.headers.get("Content-Type") ?? "";
  if (contentType.includes("application/json")) {
    try {
      return await response.json();
    } catch (error) {
      console.warn("Falha ao analisar JSON da resposta", error);
    }
  }

  return undefined;
}
