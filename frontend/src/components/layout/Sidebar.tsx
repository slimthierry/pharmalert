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
} from 'lucide-react';

const navigation = [
  { name: 'Tableau de bord', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Prescriptions', href: '/prescriptions', icon: FileText },
  { name: 'Interactions', href: '/interactions', icon: AlertTriangle },
  { name: 'Administrations', href: '/administrations', icon: Syringe },
  { name: 'Allergies', href: '/allergies', icon: ShieldAlert },
  { name: 'Effets indesirables', href: '/adverse-events', icon: Bug },
  { name: 'Audit', href: '/audit', icon: ScrollText },
];

export default function Sidebar() {
  const navigate = useNavigate();

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
      </nav>

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
