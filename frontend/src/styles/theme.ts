/**
 * PharmAlert Theme Configuration
 *
 * Brand color: Blue #3B82F6
 * Storage key: pharmalert-theme
 */

export const THEME_STORAGE_KEY = 'pharmalert-theme';

export const brandPalette = {
  50: '#EFF6FF',
  100: '#DBEAFE',
  200: '#BFDBFE',
  300: '#93C5FD',
  400: '#60A5FA',
  500: '#3B82F6',
  600: '#2563EB',
  700: '#1D4ED8',
  800: '#1E40AF',
  900: '#1E3A8A',
  950: '#172554',
} as const;

export const semanticColors = {
  light: {
    bg: {
      primary: '#ffffff',
      secondary: '#f8fafc',
      tertiary: '#f1f5f9',
      inverse: '#0f172a',
      brand: brandPalette[500],
      brandHover: brandPalette[600],
    },
    text: {
      primary: '#0f172a',
      secondary: '#475569',
      tertiary: '#94a3b8',
      inverse: '#ffffff',
      brand: brandPalette[500],
    },
    border: {
      primary: '#e2e8f0',
      secondary: '#cbd5e1',
      brand: brandPalette[500],
    },
  },
  dark: {
    bg: {
      primary: '#0f172a',
      secondary: '#1e293b',
      tertiary: '#334155',
      inverse: '#f8fafc',
      brand: brandPalette[600],
      brandHover: brandPalette[700],
    },
    text: {
      primary: '#f1f5f9',
      secondary: '#94a3b8',
      tertiary: '#64748b',
      inverse: '#0f172a',
      brand: brandPalette[400],
    },
    border: {
      primary: '#334155',
      secondary: '#475569',
      brand: brandPalette[400],
    },
  },
} as const;

export const severityColors = {
  minor: '#22c55e',
  moderate: '#f59e0b',
  major: '#f97316',
  contraindicated: '#ef4444',
  lifeThreatening: '#dc2626',
} as const;

export const statusColors = {
  active: '#22c55e',
  pending: '#f59e0b',
  suspended: '#f97316',
  cancelled: '#ef4444',
  completed: '#6366f1',
} as const;

export type ThemeMode = 'light' | 'dark';

export function getStoredTheme(): ThemeMode | null {
  if (typeof window === 'undefined') return null;
  const stored = localStorage.getItem(THEME_STORAGE_KEY);
  if (stored === 'dark' || stored === 'light') return stored;
  return null;
}

export function getPreferredTheme(): ThemeMode {
  const stored = getStoredTheme();
  if (stored) return stored;
  if (typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  return 'light';
}

export function setTheme(mode: ThemeMode): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(THEME_STORAGE_KEY, mode);
  if (mode === 'dark') {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
}

export function toggleTheme(): ThemeMode {
  const current = getPreferredTheme();
  const next = current === 'dark' ? 'light' : 'dark';
  setTheme(next);
  return next;
}
