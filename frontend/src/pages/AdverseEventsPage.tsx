import { useState, useEffect } from 'react';
import { Plus, Bug, BarChart3 } from 'lucide-react';

interface AdverseEvent {
  id: number;
  patient_ipp: string;
  medication_name: string | null;
  event_type: string;
  severity: string;
  description: string;
  outcome: string | null;
  reported_by_name: string | null;
  reported_at: string;
  status: string;
}

interface Stats {
  total: number;
  by_severity: Record<string, number>;
  by_type: Record<string, number>;
  by_status: Record<string, number>;
}

const eventTypeLabels: Record<string, string> = {
  side_effect: 'Effet secondaire',
  allergy: 'Allergie',
  overdose: 'Surdosage',
  other: 'Autre',
};

const statusLabels: Record<string, string> = {
  reported: 'Signale',
  investigating: 'En investigation',
  confirmed: 'Confirme',
  dismissed: 'Ecarte',
};

const statusColors: Record<string, string> = {
  reported: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
  investigating: 'bg-brand-100 text-brand-800 dark:bg-brand-900/30 dark:text-brand-400',
  confirmed: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  dismissed: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400',
};

export default function AdverseEventsPage() {
  const [events, setEvents] = useState<AdverseEvent[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [showStats, setShowStats] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem('pharmalert-token');
      try {
        const [eventsRes, statsRes] = await Promise.all([
          fetch('/api/v1/adverse-events/', {
            headers: { Authorization: `Bearer ${token}` },
          }),
          fetch('/api/v1/adverse-events/stats', {
            headers: { Authorization: `Bearer ${token}` },
          }),
        ]);
        if (eventsRes.ok) {
          const data = await eventsRes.json();
          setEvents(data.events);
        }
        if (statsRes.ok) setStats(await statsRes.json());
      } catch {
        // Handle error
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">
            Evenements indesirables
          </h1>
          <p className="text-sm text-[var(--color-text-secondary)]">
            Declaration et suivi des effets indesirables medicamenteux
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowStats(!showStats)}
            className="btn-secondary flex items-center gap-2"
          >
            <BarChart3 className="h-4 w-4" />
            Statistiques
          </button>
          <button className="btn-primary flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Declarer un evenement
          </button>
        </div>
      </div>

      {/* Statistics */}
      {showStats && stats && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="card">
            <p className="text-sm text-[var(--color-text-secondary)]">Total</p>
            <p className="text-3xl font-bold text-[var(--color-text-primary)]">{stats.total}</p>
          </div>
          <div className="card">
            <p className="mb-2 text-sm text-[var(--color-text-secondary)]">Par severite</p>
            {Object.entries(stats.by_severity).map(([key, val]) => (
              <div key={key} className="flex justify-between text-xs">
                <span className="text-[var(--color-text-tertiary)] capitalize">{key}</span>
                <span className="font-medium text-[var(--color-text-primary)]">{val}</span>
              </div>
            ))}
          </div>
          <div className="card">
            <p className="mb-2 text-sm text-[var(--color-text-secondary)]">Par type</p>
            {Object.entries(stats.by_type).map(([key, val]) => (
              <div key={key} className="flex justify-between text-xs">
                <span className="text-[var(--color-text-tertiary)]">{eventTypeLabels[key] || key}</span>
                <span className="font-medium text-[var(--color-text-primary)]">{val}</span>
              </div>
            ))}
          </div>
          <div className="card">
            <p className="mb-2 text-sm text-[var(--color-text-secondary)]">Par statut</p>
            {Object.entries(stats.by_status).map(([key, val]) => (
              <div key={key} className="flex justify-between text-xs">
                <span className="text-[var(--color-text-tertiary)]">{statusLabels[key] || key}</span>
                <span className="font-medium text-[var(--color-text-primary)]">{val}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Events List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600" />
        </div>
      ) : events.length === 0 ? (
        <div className="card text-center">
          <Bug className="mx-auto mb-3 h-12 w-12 text-[var(--color-text-tertiary)]" />
          <p className="text-sm text-[var(--color-text-tertiary)]">
            Aucun evenement indesirable declare
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {events.map((event) => (
            <div key={event.id} className="card">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-semibold text-[var(--color-text-primary)]">
                      {eventTypeLabels[event.event_type] || event.event_type}
                    </p>
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
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColors[event.status] || ''}`}>
                      {statusLabels[event.status] || event.status}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-[var(--color-text-secondary)]">
                    Patient: {event.patient_ipp}
                    {event.medication_name && ` | Medicament: ${event.medication_name}`}
                  </p>
                </div>
                <p className="text-xs text-[var(--color-text-tertiary)]">
                  {new Date(event.reported_at).toLocaleDateString('fr-FR')}
                </p>
              </div>
              <p className="mt-2 text-sm text-[var(--color-text-primary)]">{event.description}</p>
              {event.outcome && (
                <p className="mt-1 text-xs text-[var(--color-text-secondary)]">
                  Issue: {event.outcome}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
