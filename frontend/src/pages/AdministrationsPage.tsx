import { useState, useEffect } from 'react';
import { Clock, CheckCircle, XCircle, AlertCircle, Timer } from 'lucide-react';

interface Administration {
  id: number;
  prescription_id: number;
  nurse_name: string | null;
  scheduled_at: string;
  administered_at: string | null;
  dose_given: number | null;
  status: string;
  patient_ipp: string;
  patient_name: string | null;
  medication_name: string | null;
  notes: string | null;
}

const statusConfig: Record<string, { label: string; color: string; icon: typeof CheckCircle }> = {
  given: { label: 'Administre', color: 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/30', icon: CheckCircle },
  refused: { label: 'Refuse', color: 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/30', icon: XCircle },
  missed: { label: 'Manque', color: 'text-orange-600 bg-orange-100 dark:text-orange-400 dark:bg-orange-900/30', icon: AlertCircle },
  delayed: { label: 'Retarde', color: 'text-amber-600 bg-amber-100 dark:text-amber-400 dark:bg-amber-900/30', icon: Timer },
};

export default function AdministrationsPage() {
  const [administrations, setAdministrations] = useState<Administration[]>([]);
  const [todaySchedule, setTodaySchedule] = useState<Administration[]>([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<'today' | 'all'>('today');

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem('pharmalert-token');
      try {
        const [todayRes, allRes] = await Promise.all([
          fetch('/api/v1/administrations/today', {
            headers: { Authorization: `Bearer ${token}` },
          }),
          fetch('/api/v1/administrations/', {
            headers: { Authorization: `Bearer ${token}` },
          }),
        ]);

        if (todayRes.ok) setTodaySchedule(await todayRes.json());
        if (allRes.ok) {
          const data = await allRes.json();
          setAdministrations(data.administrations);
        }
      } catch {
        // Handle error
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const displayData = view === 'today' ? todaySchedule : administrations;

  const formatTime = (dateStr: string) => {
    return new Date(dateStr).toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">
          Administrations
        </h1>
        <p className="text-sm text-[var(--color-text-secondary)]">
          Vue infirmier - Suivi des administrations de doses
        </p>
      </div>

      {/* View Toggle */}
      <div className="flex gap-2">
        <button
          onClick={() => setView('today')}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
            view === 'today'
              ? 'bg-brand-500 text-white'
              : 'bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)]'
          }`}
        >
          Programme du jour
        </button>
        <button
          onClick={() => setView('all')}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
            view === 'all'
              ? 'bg-brand-500 text-white'
              : 'bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)]'
          }`}
        >
          Toutes les administrations
        </button>
      </div>

      {/* Timeline View */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600" />
        </div>
      ) : displayData.length === 0 ? (
        <div className="card text-center">
          <Clock className="mx-auto mb-3 h-12 w-12 text-[var(--color-text-tertiary)]" />
          <p className="text-sm text-[var(--color-text-tertiary)]">
            {view === 'today'
              ? 'Aucune administration programmee pour aujourd\'hui'
              : 'Aucune administration enregistree'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {displayData.map((admin) => {
            const config = statusConfig[admin.status] || statusConfig.missed;
            const Icon = config.icon;
            return (
              <div
                key={admin.id}
                className="card flex items-center gap-4"
              >
                {/* Time */}
                <div className="w-16 text-center">
                  <p className="text-lg font-bold text-[var(--color-text-primary)]">
                    {formatTime(admin.scheduled_at)}
                  </p>
                </div>

                {/* Status Icon */}
                <div className={`rounded-lg p-2 ${config.color}`}>
                  <Icon className="h-5 w-5" />
                </div>

                {/* Details */}
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-semibold text-[var(--color-text-primary)]">
                      {admin.medication_name || 'Medicament inconnu'}
                    </p>
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${config.color}`}>
                      {config.label}
                    </span>
                  </div>
                  <p className="text-sm text-[var(--color-text-secondary)]">
                    {admin.patient_name || admin.patient_ipp}
                    {admin.dose_given && ` - ${admin.dose_given} mg administre`}
                  </p>
                  {admin.notes && (
                    <p className="mt-1 text-xs text-[var(--color-text-tertiary)]">
                      {admin.notes}
                    </p>
                  )}
                </div>

                {/* Actions */}
                {admin.status === 'missed' && (
                  <div className="flex gap-2">
                    <button className="btn-primary text-xs">Administrer</button>
                    <button className="btn-secondary text-xs">Reporter</button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
