import { useState, useEffect, createContext, useContext } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import PrescriptionsPage from './pages/PrescriptionsPage';
import InteractionsPage from './pages/InteractionsPage';
import AdministrationsPage from './pages/AdministrationsPage';
import AllergiesPage from './pages/AllergiesPage';
import AdverseEventsPage from './pages/AdverseEventsPage';
import AuditPage from './pages/AuditPage';
import EntitiesPage from './pages/EntitiesPage';
import SettingsPage from './pages/SettingsPage';
import { EntityProvider } from './hooks/useEntity';

const STORAGE_KEY = 'pharmalert-theme';

interface ThemeContextType {
  isDark: boolean;
  toggle: () => void;
}

export const ThemeContext = createContext<ThemeContextType>({
  isDark: false,
  toggle: () => {},
});

export const useTheme = () => useContext(ThemeContext);

function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [isDark, setIsDark] = useState(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return stored === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add('dark');
      localStorage.setItem(STORAGE_KEY, 'dark');
    } else {
      root.classList.remove('dark');
      localStorage.setItem(STORAGE_KEY, 'light');
    }
  }, [isDark]);

  const toggle = () => setIsDark((prev) => !prev);

  return (
    <ThemeContext.Provider value={{ isDark, toggle }}>
      {children}
    </ThemeContext.Provider>
  );
}

function AuthGuard({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('pharmalert-token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <ThemeProvider>
      <EntityProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <AuthGuard>
                <AppLayout />
              </AuthGuard>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="prescriptions" element={<PrescriptionsPage />} />
            <Route path="interactions" element={<InteractionsPage />} />
            <Route path="administrations" element={<AdministrationsPage />} />
            <Route path="allergies" element={<AllergiesPage />} />
            <Route path="adverse-events" element={<AdverseEventsPage />} />
            <Route path="audit" element={<AuditPage />} />
            <Route path="entities" element={<EntitiesPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </EntityProvider>
    </ThemeProvider>
  );
}
