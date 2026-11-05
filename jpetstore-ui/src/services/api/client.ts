import axios from "axios";
import { STORAGE_KEYS } from "@/utils/cn";
import type { ApiErrorBody } from "@/types/api";
import {
  apiBaseUrl,
  getApiConfigError,
  logApiConfigInDev,
  useMockApi,
} from "@/services/api/config";

export { useMockApi };

logApiConfigInDev();

export const apiClient = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

apiClient.interceptors.request.use((config) => {
  if (!useMockApi && getApiConfigError()) {
    return Promise.reject(new Error(getApiConfigError() ?? "Invalid API configuration"));
  }
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
  const configError = getApiConfigError();
  if (configError && !useMockApi) {
    return configError;
  }
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as ApiErrorBody | undefined;
    if (data?.error?.message) return data.error.message;
    if (error.response?.status === 404) {
      return "The requested resource was not found on the API.";
    }
    if (error.response?.status === 0 || error.code === "ERR_NETWORK") {
      return (
        "Cannot reach the API. Confirm the backend is running, VITE_API_BASE_URL is correct, " +
        "and CORS allows this browser origin."
      );
    }
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
