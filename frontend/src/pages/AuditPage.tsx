import { useState, useEffect } from 'react';
import { Search, ScrollText, Filter } from 'lucide-react';

interface AuditLog {
  id: number;
  user_id: number | null;
  user_name: string | null;
  action: string;
  entity_type: string;
  entity_id: string | null;
  details: Record<string, unknown> | null;
  ip_address: string | null;
  timestamp: string;
}

export default function AuditPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState({
    action: '',
    entity_type: '',
  });

  const fetchLogs = async () => {
    try {
      const token = localStorage.getItem('pharmalert-token');
      const params = new URLSearchParams();
      if (filters.action) params.set('action', filters.action);
      if (filters.entity_type) params.set('entity_type', filters.entity_type);
      params.set('limit', '50');

      const response = await fetch(`/api/v1/audit/?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setLogs(data.logs);
        setTotal(data.total);
      }
    } catch {
      // Handle error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const formatTimestamp = (ts: string) => {
    return new Date(ts).toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">
          Piste d'audit
        </h1>
        <p className="text-sm text-[var(--color-text-secondary)]">
          Journal complet de toutes les actions effectuees dans le systeme
        </p>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
          <input
            type="text"
            placeholder="Filtrer par action..."
            value={filters.action}
            onChange={(e) => setFilters({ ...filters, action: e.target.value })}
            onKeyDown={(e) => e.key === 'Enter' && fetchLogs()}
            className="input-field pl-10"
          />
        </div>
        <select
          value={filters.entity_type}
          onChange={(e) => setFilters({ ...filters, entity_type: e.target.value })}
          className="input-field w-48"
        >
          <option value="">Tous les types</option>
          <option value="prescription">Prescription</option>
          <option value="administration">Administration</option>
          <option value="adverse_event">Evenement indesirable</option>
          <option value="api_request">Requete API</option>
        </select>
        <button onClick={fetchLogs} className="btn-secondary flex items-center gap-2">
          <Filter className="h-4 w-4" />
          Filtrer
        </button>
      </div>

      <p className="text-sm text-[var(--color-text-tertiary)]">
        {total} entree(s) trouvee(s)
      </p>

      {/* Audit Logs Table */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600" />
        </div>
      ) : logs.length === 0 ? (
        <div className="card text-center">
          <ScrollText className="mx-auto mb-3 h-12 w-12 text-[var(--color-text-tertiary)]" />
          <p className="text-sm text-[var(--color-text-tertiary)]">
            Aucune entree d'audit trouvee
          </p>
        </div>
      ) : (
        <div className="card overflow-hidden p-0">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[var(--color-border-primary)] bg-[var(--color-bg-secondary)]">
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-[var(--color-text-secondary)]">
                  Horodatage
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-[var(--color-text-secondary)]">
                  Utilisateur
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-[var(--color-text-secondary)]">
                  Action
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-[var(--color-text-secondary)]">
                  Type
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-[var(--color-text-secondary)]">
                  ID Entite
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-[var(--color-text-secondary)]">
                  IP
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-border-primary)]">
              {logs.map((log) => (
                <tr key={log.id} className="transition-colors hover:bg-[var(--color-bg-secondary)]">
                  <td className="px-4 py-3 text-xs font-mono text-[var(--color-text-secondary)]">
                    {formatTimestamp(log.timestamp)}
                  </td>
                  <td className="px-4 py-3 text-sm text-[var(--color-text-primary)]">
                    {log.user_name || (log.user_id ? `User #${log.user_id}` : 'Anonyme')}
                  </td>
                  <td className="px-4 py-3 text-sm text-[var(--color-text-primary)]">
                    <code className="rounded bg-[var(--color-bg-tertiary)] px-1.5 py-0.5 text-xs">
                      {log.action}
                    </code>
                  </td>
                  <td className="px-4 py-3 text-sm text-[var(--color-text-secondary)]">
                    {log.entity_type}
                  </td>
                  <td className="px-4 py-3 text-sm font-mono text-[var(--color-text-tertiary)]">
                    {log.entity_id || '-'}
                  </td>
                  <td className="px-4 py-3 text-xs font-mono text-[var(--color-text-tertiary)]">
                    {log.ip_address || '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
