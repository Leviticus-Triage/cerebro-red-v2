/**
 * Authentication store using Zustand.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { apiClient } from '@/lib/api/client';
import { wsClient } from '@/lib/websocket/client';

interface AuthState {
  apiKey: string | null;
  isAuthenticated: boolean;
  setApiKey: (key: string) => void;
  clearApiKey: () => void;
  checkAuth: () => Promise<boolean>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      apiKey: null,
      isAuthenticated: false,
      setApiKey: (key) => {
        apiClient.setApiKey(key);
        wsClient.setApiKey(key);
        set({ apiKey: key, isAuthenticated: true });
      },
      clearApiKey: () => {
        apiClient.clearApiKey();
        wsClient.setApiKey(null);
        set({ apiKey: null, isAuthenticated: false });
      },
      checkAuth: async () => {
        try {
          await apiClient.healthCheck();
          return true;
        } catch {
          return false;
        }
      },
    }),
    {
      name: 'cerebro-auth',
    }
  )
);
