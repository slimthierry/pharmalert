import { useState, useEffect } from 'react';
import {
  FileCheck,
  AlertTriangle,
  Clock,
  TrendingUp,
  Activity,
  Users,
} from 'lucide-react';

interface DashboardStats {
  pending_validations: number;
  critical_interactions: number;
  missed_doses_today: number;
  compliance_rate: number;
  total_active_prescriptions: number;
  total_patients: number;
}

interface DashboardData {
  stats: DashboardStats;
  alerts: {
    critical_interactions: unknown[];
    recent_adverse_events: unknown[];
  };
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = localStorage.getItem('pharmalert-token');
        const response = await fetch('/api/v1/dashboard/', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (response.ok) {
          setData(await response.json());
        }
      } catch {
        // Handle error silently
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  const stats = data?.stats;

  const statCards = [
    {
      label: 'Validations en attente',
      value: stats?.pending_validations ?? 0,
      icon: FileCheck,
      color: 'text-amber-600 bg-amber-100 dark:text-amber-400 dark:bg-amber-900/30',
    },
    {
      label: 'Alertes interactions',
      value: stats?.critical_interactions ?? 0,
      icon: AlertTriangle,
      color: 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/30',
      critical: true,
    },
    {
      label: 'Doses manquees (aujourd\'hui)',
      value: stats?.missed_doses_today ?? 0,
      icon: Clock,
      color: 'text-orange-600 bg-orange-100 dark:text-orange-400 dark:bg-orange-900/30',
    },
    {
      label: 'Taux de conformite',
      value: `${stats?.compliance_rate ?? 100}%`,
      icon: TrendingUp,
      color: 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/30',
    },
    {
      label: 'Prescriptions actives',
      value: stats?.total_active_prescriptions ?? 0,
      icon: Activity,
      color: 'text-brand-600 bg-brand-100 dark:text-brand-400 dark:bg-brand-900/30',
    },
    {
      label: 'Patients suivis',
      value: stats?.total_patients ?? 0,
      icon: Users,
      color: 'text-indigo-600 bg-indigo-100 dark:text-indigo-400 dark:bg-indigo-900/30',
    },
  ];

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">
          Tableau de bord
        </h1>
        <p className="text-sm text-[var(--color-text-secondary)]">
          Vue d'ensemble de l'activite pharmaceutique
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {statCards.map((stat) => (
          <div key={stat.label} className="card">
            <div className="flex items-center gap-4">
              <div className={`rounded-lg p-3 ${stat.color}`}>
                <stat.icon className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm text-[var(--color-text-secondary)]">
                  {stat.label}
                </p>
                <p
                  className={`text-2xl font-bold ${
                    stat.critical && (stats?.critical_interactions ?? 0) > 0
                      ? 'text-red-600 dark:text-red-400'
                      : 'text-[var(--color-text-primary)]'
                  }`}
                >
                  {stat.value}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Adverse Events */}
      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-[var(--color-text-primary)]">
          Evenements indesirables recents
        </h2>
        {data?.alerts.recent_adverse_events &&
        data.alerts.recent_adverse_events.length > 0 ? (
          <div className="space-y-3">
            {(data.alerts.recent_adverse_events as Array<{
              id: number;
              patient_ipp: string;
              severity: string;
              description: string;
              status: string;
            }>).map((event) => (
              <div
                key={event.id}
                className="flex items-center justify-between rounded-lg border border-[var(--color-border-primary)] p-3"
              >
                <div>
                  <p className="text-sm font-medium text-[var(--color-text-primary)]">
                    Patient {event.patient_ipp}
                  </p>
                  <p className="text-xs text-[var(--color-text-secondary)]">
                    {event.description}
                  </p>
                </div>
                <span
                  className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
                    event.severity === 'life_threatening' || event.severity === 'serious'
                      ? 'severity-contraindicated'
                      : event.severity === 'moderate'
                        ? 'severity-moderate'
                        : 'severity-minor'
                  }`}
                >
                  {event.severity}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-[var(--color-text-tertiary)]">
            Aucun evenement indesirable recent
          </p>
        )}
      </div>
    </div>
  );
}
