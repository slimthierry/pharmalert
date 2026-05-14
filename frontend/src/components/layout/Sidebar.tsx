import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  AlertTriangle,
  Syringe,
  ShieldAlert,
  Bug,
  ScrollText,
  LogOut,
  Pill,
  Building2,
  Settings,
  ChevronDown,
} from 'lucide-react';
import { useEntity } from '../../hooks/useEntity';
import { UserRole } from '../../types';

const navigation = [
  { name: 'Tableau de bord', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Prescriptions', href: '/prescriptions', icon: FileText },
  { name: 'Interactions', href: '/interactions', icon: AlertTriangle },
  { name: 'Administrations', href: '/administrations', icon: Syringe },
  { name: 'Allergies', href: '/allergies', icon: ShieldAlert },
  { name: 'Effets indesirables', href: '/adverse-events', icon: Bug },
  { name: 'Audit', href: '/audit', icon: ScrollText },
];

const adminNavigation = [
  { name: 'Etablissements', href: '/entities', icon: Building2 },
  { name: 'Parametres', href: '/settings', icon: Settings },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const { currentEntity, entities, switchEntity } = useEntity();

  // Check if user is admin
  const userData = localStorage.getItem('pharmalert-user');
  const user = userData ? JSON.parse(userData) : null;
  const isAdmin = user?.role === UserRole.ADMIN;

  const handleLogout = () => {
    localStorage.removeItem('pharmalert-token');
    localStorage.removeItem('pharmalert-user');
    navigate('/login');
  };

  return (
    <aside className="flex w-64 flex-col border-r border-[var(--color-border-primary)] bg-[var(--color-bg-primary)]">
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 border-b border-[var(--color-border-primary)] px-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-500">
          <Pill className="h-5 w-5 text-white" />
        </div>
        <span className="text-lg font-bold text-[var(--color-text-primary)]">
          PharmAlert
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-brand-50 text-brand-700 dark:bg-brand-950 dark:text-brand-400'
                  : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-tertiary)] hover:text-[var(--color-text-primary)]'
              }`
            }
          >
            <item.icon className="h-5 w-5" />
            {item.name}
          </NavLink>
        ))}

        {/* Admin section */}
        {isAdmin && (
          <>
            <div className="pt-4 pb-1">
              <span className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Administration
              </span>
            </div>
            {adminNavigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-brand-50 text-brand-700 dark:bg-brand-950 dark:text-brand-400'
                      : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-tertiary)] hover:text-[var(--color-text-primary)]'
                  }`
                }
              >
                <item.icon className="h-5 w-5" />
                {item.name}
              </NavLink>
            ))}
          </>
        )}
      </nav>

      {/* Entity Selector */}
      {entities.length > 0 && (
        <div className="border-t border-[var(--color-border-primary)] px-3 py-3">
          <div className="relative">
            <select
              value={currentEntity?.id || ''}
              onChange={(e) => switchEntity(parseInt(e.target.value))}
              className="w-full appearance-none px-3 py-2 pr-8 text-sm bg-[var(--color-bg-tertiary)] border border-[var(--color-border-primary)] rounded-lg focus:ring-2 focus:ring-brand-500"
            >
              {entities.map((entity) => (
                <option key={entity.id} value={entity.id}>
                  {entity.name}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
          </div>
        </div>
      )}

      {/* Logout */}
      <div className="border-t border-[var(--color-border-primary)] p-3">
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-[var(--color-text-secondary)] transition-colors hover:bg-[var(--color-bg-tertiary)] hover:text-red-600"
        >
          <LogOut className="h-5 w-5" />
          Deconnexion
        </button>
      </div>
    </aside>
  );
}
