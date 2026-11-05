import axios from "axios";
import { STORAGE_KEYS } from "@/utils/cn";
import type { ApiErrorBody } from "@/types/api";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "";

/** Use mock fixtures only when explicitly enabled (never silent fallback in production). */
export const useMockApi = import.meta.env.VITE_USE_MOCK_API === "true";

export const apiClient = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(STORAGE_KEYS.accessToken);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      localStorage.removeItem(STORAGE_KEYS.accessToken);
    }
    return Promise.reject(error);
  },
);

export function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as ApiErrorBody | undefined;
    if (data?.error?.message) return data.error.message;
    if (error.response?.status === 401) {
      return "Please sign on to continue.";
    }
    if (error.message) return error.message;
  }
  if (error instanceof Error) return error.message;
  return "Something went wrong. Please try again.";
}

export function isApiErrorCode(error: unknown, code: string): boolean {
  if (!axios.isAxiosError(error)) return false;
  const data = error.response?.data as ApiErrorBody | undefined;
  return data?.error?.code === code;
}
