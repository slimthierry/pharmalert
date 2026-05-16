import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import * as SecureStore from 'expo-secure-store';
import { api, getBaseUrl } from '../services/api';
import type { User, TokenResponse } from '../types';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setTokenState] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Restore session on mount
  useEffect(() => {
    const restore = async () => {
      try {
        const storedToken = await SecureStore.getItemAsync('pharmalert_token');
        if (storedToken) {
          await SecureStore.setItemAsync('pharmalert_token', storedToken); // keep it
          const me = await api.me();
          setUser(me);
          setTokenState(storedToken);
        }
      } catch {
        // Token expired or invalid — silently clear it without showing error
        await SecureStore.deleteItemAsync('pharmalert_token');
      } finally {
        setIsLoading(false);
      }
    };
    restore();
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    console.log('🔐 LOGIN: Tentative pour', email);
    const baseUrl = await getBaseUrl();
    console.log('🔐 LOGIN: URL backend:', baseUrl);

    let res: TokenResponse;
    try {
      res = await api.login(email, password);
      console.log('✅ LOGIN: Token reçu', res.access_token?.substring(0, 20) + '...');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error('❌ LOGIN: Erreur:', msg);
      throw new Error(msg);
    }

    await SecureStore.setItemAsync('pharmalert_token', res.access_token);
    await SecureStore.setItemAsync('pharmalert_user_name', res.name);
    await SecureStore.setItemAsync('pharmalert_user_role', res.role);
    setTokenState(res.access_token);

    try {
      const me = await api.me();
      console.log('✅ LOGIN: Utilisateur chargé:', me.name);
      setUser(me);
    } catch (err: unknown) {
      console.error('❌ LOGIN: Erreur me():', err);
    }
  }, []);

  const logout = useCallback(async () => {
    await api.logout();
    await SecureStore.deleteItemAsync('pharmalert_token');
    setUser(null);
    setTokenState(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, token, isLoading, isAuthenticated: !!token, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
