import type {
  TokenResponse,
  User,
  Medication,
  Prescription,
  Administration,
  PatientAllergy,
  AdverseEvent,
  AuditLog,
  Interaction,
  InteractionCheckResponse,
  DashboardResponse,
} from '@pharmalert/types';

const API_BASE = '/api/v1';

class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
    this.name = 'ApiError';
  }
}

function getHeaders(): HeadersInit {
  const token = localStorage.getItem('pharmalert-token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...getHeaders(),
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({ detail: 'Erreur inconnue' }));
    throw new ApiError(response.status, data.detail || 'Erreur serveur');
  }

  if (response.status === 204) return undefined as T;
  return response.json();
}

// ========================
// Auth
// ========================

export const auth = {
  login: (email: string, password: string) =>
    request<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  me: () => request<User>('/auth/me'),

  register: (data: { email: string; name: string; password: string; role: string }) =>
    request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// ========================
// Medications
// ========================

export const medications = {
  list: (params?: { search?: string; atc_code?: string; skip?: number; limit?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.search) searchParams.set('search', params.search);
    if (params?.atc_code) searchParams.set('atc_code', params.atc_code);
    if (params?.skip) searchParams.set('skip', String(params.skip));
    if (params?.limit) searchParams.set('limit', String(params.limit));
    return request<{ medications: Medication[]; total: number }>(`/medications/?${searchParams}`);
  },

  get: (id: number) => request<Medication>(`/medications/${id}`),

  create: (data: Partial<Medication>) =>
    request<Medication>('/medications/', { method: 'POST', body: JSON.stringify(data) }),

  update: (id: number, data: Partial<Medication>) =>
    request<Medication>(`/medications/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  delete: (id: number) =>
    request<void>(`/medications/${id}`, { method: 'DELETE' }),
};

// ========================
// Prescriptions
// ========================

export const prescriptions = {
  list: (params?: { patient_ipp?: string; status?: string; validation_status?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.patient_ipp) searchParams.set('patient_ipp', params.patient_ipp);
    if (params?.status) searchParams.set('status', params.status);
    if (params?.validation_status) searchParams.set('validation_status', params.validation_status);
    return request<{ prescriptions: Prescription[]; total: number }>(`/prescriptions/?${searchParams}`);
  },

  get: (id: number) => request<Prescription>(`/prescriptions/${id}`),

  create: (data: Record<string, unknown>) =>
    request<{ prescription: Prescription; interactions: unknown[]; allergy_warnings: string[] }>(
      '/prescriptions/',
      { method: 'POST', body: JSON.stringify(data) },
    ),

  validate: (id: number, data: { validation_status: string; validation_notes?: string }) =>
    request<Prescription>(`/prescriptions/${id}/validate`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// ========================
// Interactions
// ========================

export const interactions = {
  list: (params?: { severity?: string; medication_id?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.severity) searchParams.set('severity', params.severity);
    if (params?.medication_id) searchParams.set('medication_id', String(params.medication_id));
    return request<{ interactions: Interaction[]; total: number }>(`/interactions/?${searchParams}`);
  },

  check: (medication_ids: number[], patient_ipp?: string) =>
    request<InteractionCheckResponse>('/interactions/check', {
      method: 'POST',
      body: JSON.stringify({ medication_ids, patient_ipp }),
    }),

  matrix: (medication_ids: number[]) =>
    request<unknown>('/interactions/matrix', {
      method: 'POST',
      body: JSON.stringify(medication_ids),
    }),
};

// ========================
// Administrations
// ========================

export const administrations = {
  list: (params?: { patient_ipp?: string; status?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.patient_ipp) searchParams.set('patient_ipp', params.patient_ipp);
    if (params?.status) searchParams.set('status', params.status);
    return request<{ administrations: Administration[]; total: number }>(`/administrations/?${searchParams}`);
  },

  today: () => request<Administration[]>('/administrations/today'),

  record: (id: number, data: { status: string; dose_given?: number; notes?: string }) =>
    request<Administration>(`/administrations/${id}/record`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// ========================
// Allergies
// ========================

export const allergies = {
  list: (params?: { patient_ipp?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.patient_ipp) searchParams.set('patient_ipp', params.patient_ipp);
    return request<{ allergies: PatientAllergy[]; total: number }>(`/allergies/?${searchParams}`);
  },

  patientAllergies: (patient_ipp: string) =>
    request<PatientAllergy[]>(`/allergies/patient/${patient_ipp}`),

  create: (data: Record<string, unknown>) =>
    request<PatientAllergy>('/allergies/', { method: 'POST', body: JSON.stringify(data) }),

  delete: (id: number) =>
    request<void>(`/allergies/${id}`, { method: 'DELETE' }),
};

// ========================
// Adverse Events
// ========================

export const adverseEvents = {
  list: (params?: { patient_ipp?: string; severity?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.patient_ipp) searchParams.set('patient_ipp', params.patient_ipp);
    if (params?.severity) searchParams.set('severity', params.severity);
    return request<{ events: AdverseEvent[]; total: number }>(`/adverse-events/?${searchParams}`);
  },

  stats: () =>
    request<{ total: number; by_severity: Record<string, number>; by_type: Record<string, number>; by_status: Record<string, number> }>(
      '/adverse-events/stats',
    ),

  create: (data: Record<string, unknown>) =>
    request<AdverseEvent>('/adverse-events/', { method: 'POST', body: JSON.stringify(data) }),

  update: (id: number, data: Record<string, unknown>) =>
    request<AdverseEvent>(`/adverse-events/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
};

// ========================
// Dashboard
// ========================

export const dashboard = {
  get: () => request<DashboardResponse>('/dashboard/'),
};

// ========================
// Audit
// ========================

export const audit = {
  list: (params?: { action?: string; entity_type?: string; user_id?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.action) searchParams.set('action', params.action);
    if (params?.entity_type) searchParams.set('entity_type', params.entity_type);
    if (params?.user_id) searchParams.set('user_id', String(params.user_id));
    return request<{ logs: AuditLog[]; total: number }>(`/audit/?${searchParams}`);
  },
};

export { ApiError };
