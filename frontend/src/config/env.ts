const DEFAULT_API_BASE_URL = "http://localhost:5000";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL;

export const env = {
  apiBaseUrl,
} as const;
