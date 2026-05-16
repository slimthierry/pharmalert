import * as SecureStore from 'expo-secure-store';
import type {
  TokenResponse,
  User,
  Medication,
  Prescription,
  Administration,
  PatientAllergy,
  Interaction,
  InteractionCheckResponse,
  DashboardResponse,
  EntityBrief,
  SIHStatus,
} from '../types';

// ─── Config ───────────────────────────────────────────────────────────────────

// L'URL est configurable — par défaut backend Docker
// Utilise SecureStore pour conserver le choix de l'utilisateur
const DEFAULT_BASE_URL = 'https://9f6210f6a36df0f0-102-64-167-178.serveousercontent.com/api/v1';

const KEY_BASE_URL = 'pharmalert_base_url';
const KEY_TOKEN = 'pharmalert_token';

export async function getBaseUrl(): Promise<string> {
  try {
    const stored = await SecureStore.getItemAsync(KEY_BASE_URL);
    if (stored) return stored;
  } catch { /* ignore */ }
  return DEFAULT_BASE_URL;
}

export async function setBaseUrl(url: string): Promise<void> {
  await SecureStore.setItemAsync(KEY_BASE_URL, url);
}

async function resetBaseUrl(): Promise<void> {
  try {
    const stored = await SecureStore.getItemAsync(KEY_BASE_URL);
    if (stored && stored !== DEFAULT_BASE_URL) {
      console.log('🔄 Reset URL stockée:', stored, '->', DEFAULT_BASE_URL);
      await SecureStore.deleteItemAsync(KEY_BASE_URL);
    }
  } catch { /* ignore */ }
}
resetBaseUrl();

async function getToken(): Promise<string | null> {
  try {
    return await SecureStore.getItemAsync(KEY_TOKEN);
  } catch {
    return null;
  }
}

async function setToken(token: string | null): Promise<void> {
  if (token) {
    await SecureStore.setItemAsync(KEY_TOKEN, token);
  } else {
    await SecureStore.deleteItemAsync(KEY_TOKEN);
  }
}

// ─── API Client ───────────────────────────────────────────────────────────────

class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
    this.name = 'ApiError';
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = await getToken();
  const baseUrl = await getBaseUrl();
  const url = `${baseUrl}${path}`;
  console.log('🌐 REQUEST:', options.method || 'GET', url);

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });

  console.log('🌐 RESPONSE:', response.status, url);

  if (!response.ok) {
    const text = await response.text();
    console.error('❌ REQUEST ERROR:', response.status, text.substring(0, 200));
    let data = { detail: 'Erreur serveur' };
    try { data = JSON.parse(text || '{}'); } catch { /* ignore */ }
    throw new ApiError(response.status, data.detail || `HTTP ${response.status}`);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

export const api = {
  // Auth
  login: (email: string, password: string) =>
    request<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  me: () => request<User>('/auth/me'),

  logout: async () => {
    await setToken(null);
  },

  // Dashboard
  getDashboard: () => request<DashboardResponse>('/dashboard/'),

  // Medications
  getMedications: (skip = 0, limit = 50, search?: string) => {
    const params = new URLSearchParams({ skip: String(skip), limit: String(limit) });
    if (search) params.set('search', search);
    return request<{ items: Medication[]; total: number }>(`/medications/?${params}`);
  },

  getMedication: (id: number) =>
    request<Medication>(`/medications/${id}`),

  // Prescriptions
  getPrescriptions: (skip = 0, limit = 50, status?: string) => {
    const params = new URLSearchParams({ skip: String(skip), limit: String(limit) });
    if (status) params.set('status', status);
    return request<{ items: Prescription[]; total: number }>(`/prescriptions/?${params}`);
  },

  getPrescription: (id: number) =>
    request<Prescription>(`/prescriptions/${id}`),

  createPrescription: (data: Partial<Prescription>) =>
    request<Prescription>('/prescriptions/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Administrations
  getAdministrations: (skip = 0, limit = 50) => {
    const params = new URLSearchParams({ skip: String(skip), limit: String(limit) });
    return request<{ items: Administration[]; total: number }>(`/administrations/?${params}`);
  },

  createAdministration: (data: Partial<Administration>) =>
    request<Administration>('/administrations/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Allergies
  getAllergies: (skip = 0, limit = 50) => {
    const params = new URLSearchParams({ skip: String(skip), limit: String(limit) });
    return request<{ items: PatientAllergy[]; total: number }>(`/allergies/?${params}`);
  },

  createAllergy: (data: Partial<PatientAllergy>) =>
    request<PatientAllergy>('/allergies/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Interactions
  checkInteractions: (medicationIds: number[]) =>
    request<InteractionCheckResponse>('/interactions/check', {
      method: 'POST',
      body: JSON.stringify({ medication_ids: medicationIds }),
    }),

  getInteractions: (skip = 0, limit = 50) => {
    const params = new URLSearchParams({ skip: String(skip), limit: String(limit) });
    return request<{ items: Interaction[]; total: number }>(`/interactions/?${params}`);
  },

  // Entities
  getEntities: () => request<{ entities: EntityBrief[]; total: number }>('/entities/'),

  getMyEntities: () => request<EntityBrief[]>('/entities/me/entities'),

  getMyDefaultEntity: () => request<EntityBrief | null>('/entities/me/default-entity'),

  // SIH Sync
  getSIHStatus: () => request<SIHStatus>('/sih/status'),

  syncAll: () => request<{ success: boolean; stats: Record<string, unknown> }>('/sih/sync/all', { method: 'POST' }),
};

export { setToken, ApiError };
