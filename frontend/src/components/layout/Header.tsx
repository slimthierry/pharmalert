import { useTheme } from '../../App';
import { Moon, Sun, Bell, User } from 'lucide-react';

function ThemeToggleIcon() {
  const { isDark, toggle } = useTheme();

  return (
    <button
      onClick={toggle}
      className="rounded-lg p-2 text-[var(--color-text-secondary)] transition-colors hover:bg-[var(--color-bg-tertiary)] hover:text-[var(--color-text-primary)]"
      aria-label="Basculer le theme"
    >
      {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
    </button>
  );
}

export default function Header() {
  const user = JSON.parse(localStorage.getItem('pharmalert-user') || '{}');

  const roleLabels: Record<string, string> = {
    admin: 'Administrateur',
    medecin: 'Medecin',
    pharmacien: 'Pharmacien',
    infirmier: 'Infirmier',
    preparateur: 'Preparateur',
  };

  return (
    <header className="flex h-16 items-center justify-between border-b border-[var(--color-border-primary)] bg-[var(--color-bg-primary)] px-6">
      <div>
        <h2 className="text-sm font-medium text-[var(--color-text-secondary)]">
          Module SIH - Gestion des interactions medicamenteuses
        </h2>
      </div>

      <div className="flex items-center gap-3">
        {/* Notifications */}
        <button className="relative rounded-lg p-2 text-[var(--color-text-secondary)] transition-colors hover:bg-[var(--color-bg-tertiary)] hover:text-[var(--color-text-primary)]">
          <Bell className="h-5 w-5" />
          <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-red-500" />
        </button>

        {/* Theme toggle */}
        <ThemeToggleIcon />

        {/* User info */}
        <div className="flex items-center gap-3 rounded-lg border border-[var(--color-border-primary)] px-3 py-1.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 dark:bg-brand-900">
            <User className="h-4 w-4 text-brand-600 dark:text-brand-400" />
          </div>
          <div>
            <p className="text-sm font-medium text-[var(--color-text-primary)]">
              {user.name || 'Utilisateur'}
            </p>
            <p className="text-xs text-[var(--color-text-tertiary)]">
              {roleLabels[user.role] || user.role || 'Role inconnu'}
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
