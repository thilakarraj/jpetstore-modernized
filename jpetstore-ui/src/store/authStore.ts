import { create } from "zustand";
import { persist } from "zustand/middleware";
import {
  fetchAccountProfile,
  login as loginRequest,
  logoutLocal,
  register as registerRequest,
} from "@/services/api/authService";
import { getApiErrorMessage } from "@/services/api/client";
import type { AccountProfile, LoginPayload, RegisterPayload } from "@/types/api";
import { STORAGE_KEYS } from "@/utils/cn";

interface AuthState {
  user: AccountProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  loadProfile: () => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      clearError: () => set({ error: null }),
      login: async (payload) => {
        set({ isLoading: true, error: null });
        try {
          await loginRequest(payload);
          const profile = await fetchAccountProfile();
          set({ user: profile, isAuthenticated: true, isLoading: false });
          const { useCartStore } = await import("@/store/cartStore");
          void useCartStore.getState().refreshCart();
        } catch (e) {
          logoutLocal();
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: getApiErrorMessage(e),
          });
          throw e;
        }
      },
      register: async (payload) => {
        set({ isLoading: true, error: null });
        try {
          await registerRequest(payload);
          set({ isLoading: false });
        } catch (e) {
          set({ isLoading: false, error: getApiErrorMessage(e) });
          throw e;
        }
      },
      loadProfile: async () => {
        const token = localStorage.getItem(STORAGE_KEYS.accessToken);
        if (!token) {
          set({ user: null, isAuthenticated: false });
          return;
        }
        set({ isLoading: true });
        try {
          const profile = await fetchAccountProfile();
          set({ user: profile, isAuthenticated: true, isLoading: false, error: null });
          const { useCartStore } = await import("@/store/cartStore");
          void useCartStore.getState().refreshCart();
        } catch {
          logoutLocal();
          set({ user: null, isAuthenticated: false, isLoading: false });
        }
      },
      logout: () => {
        logoutLocal();
        set({ user: null, isAuthenticated: false, error: null });
      },
    }),
    {
      name: "jpetstore-auth",
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
);
