import { apiClient, useMockApi } from "@/services/api/client";
import { STORAGE_KEYS } from "@/utils/cn";
import type {
  AccountProfile,
  AuthLoginResponse,
  LoginPayload,
  RegisterPayload,
} from "@/types/api";

export async function login(payload: LoginPayload): Promise<AuthLoginResponse> {
  if (useMockApi) {
    await delay(250);
    if (payload.username === "j2ee" && payload.password === "j2ee") {
      const data: AuthLoginResponse = {
        access_token: "mock-jwt-token",
        token_type: "bearer",
        expires_in: 3600,
      };
      localStorage.setItem(STORAGE_KEYS.accessToken, data.access_token);
      return data;
    }
    const err = new Error("Invalid username or password. Signon failed.");
    throw err;
  }
  const { data } = await apiClient.post<AuthLoginResponse>(
    "/api/v1/auth/login",
    payload,
  );
  localStorage.setItem(STORAGE_KEYS.accessToken, data.access_token);
  return data;
}

export async function register(payload: RegisterPayload): Promise<{ username: string }> {
  if (useMockApi) {
    await delay(300);
    return { username: payload.username };
  }
  const { data } = await apiClient.post<{ username: string }>(
    "/api/v1/auth/register",
    payload,
  );
  return data;
}

export async function fetchAccountProfile(): Promise<AccountProfile> {
  if (useMockApi) {
    const token = localStorage.getItem(STORAGE_KEYS.accessToken);
    if (!token) throw new Error("Unauthorized");
    await delay(150);
    return mockProfileData;
  }
  const { data } = await apiClient.get<AccountProfile>("/api/v1/account/me");
  return data;
}

export async function updateAccountProfile(
  partial: Partial<AccountProfile> & { password?: string },
): Promise<AccountProfile> {
  if (useMockApi) {
    await delay(200);
    mockProfileData = { ...mockProfileData, ...partial };
    return mockProfileData;
  }
  const { data } = await apiClient.put<AccountProfile>("/api/v1/account/me", partial);
  return data;
}

export function logoutLocal(): void {
  localStorage.removeItem(STORAGE_KEYS.accessToken);
}

let mockProfileData: AccountProfile = {
  username: "j2ee",
  email: "j2ee@example.com",
  first_name: "J",
  last_name: "EE",
  address1: "901 San Antonio Road",
  city: "Palo Alto",
  state: "CA",
  zip: "94303",
  country: "USA",
  phone: "555-8102",
  language_preference: "english",
  favourite_category_id: "DOGS",
  list_option: true,
  banner_option: true,
  banner_name: "Golden Retriever",
};

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
