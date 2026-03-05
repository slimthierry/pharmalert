import { useState, useEffect } from 'react';
import { Search, AlertTriangle, ShieldCheck, ShieldAlert, ShieldX } from 'lucide-react';

interface Interaction {
  id: number;
  medication_a_id: number;
  medication_a_name: string | null;
  medication_b_id: number;
  medication_b_name: string | null;
  severity: string;
  mechanism: string | null;
  clinical_effect: string;
  recommendation: string;
  source: string | null;
}

interface CheckResult {
  interactions: Interaction[];
  has_contraindicated: boolean;
  has_major: boolean;
  allergy_warnings: string[];
}

const severityConfig: Record<string, { label: string; color: string; icon: typeof ShieldCheck }> = {
  minor: { label: 'Mineure', color: 'severity-minor', icon: ShieldCheck },
  moderate: { label: 'Moderee', color: 'severity-moderate', icon: ShieldAlert },
  major: { label: 'Majeure', color: 'severity-major', icon: ShieldX },
  contraindicated: { label: 'Contre-indiquee', color: 'severity-contraindicated', icon: ShieldX },
};

export default function InteractionsPage() {
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [checkResult, setCheckResult] = useState<CheckResult | null>(null);
  const [selectedMeds, setSelectedMeds] = useState('');

  useEffect(() => {
    const fetchInteractions = async () => {
      try {
        const token = localStorage.getItem('pharmalert-token');
        const response = await fetch('/api/v1/interactions/', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (response.ok) {
          const data = await response.json();
          setInteractions(data.interactions);
        }
      } catch {
        // Handle error
      } finally {
        setLoading(false);
      }
    };
    fetchInteractions();
  }, []);

  const handleCheck = async () => {
    const ids = selectedMeds.split(',').map((s) => parseInt(s.trim())).filter((n) => !isNaN(n));
    if (ids.length < 2) return;

    try {
      const token = localStorage.getItem('pharmalert-token');
      const response = await fetch('/api/v1/interactions/check', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ medication_ids: ids }),
      });
      if (response.ok) {
        setCheckResult(await response.json());
      }
    } catch {
      // Handle error
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">
          Interactions medicamenteuses
        </h1>
        <p className="text-sm text-[var(--color-text-secondary)]">
          Base de donnees et outil de verification des interactions
        </p>
      </div>

      {/* Interaction Checker Tool */}
      <div className="card border-brand-200 dark:border-brand-800">
        <h2 className="mb-4 text-lg font-semibold text-[var(--color-text-primary)]">
          Verificateur d'interactions
        </h2>
        <p className="mb-3 text-sm text-[var(--color-text-secondary)]">
          Entrez les IDs des medicaments separes par des virgules pour verifier les interactions.
        </p>
        <div className="flex gap-3">
          <input
            type="text"
            value={selectedMeds}
            onChange={(e) => setSelectedMeds(e.target.value)}
            placeholder="Ex: 1, 2, 3"
            className="input-field flex-1"
          />
          <button onClick={handleCheck} className="btn-primary flex items-center gap-2">
            <Search className="h-4 w-4" />
            Verifier
          </button>
        </div>

        {/* Check Results */}
        {checkResult && (
          <div className="mt-4 space-y-3">
            {checkResult.has_contraindicated && (
              <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-800 dark:bg-red-900/20 dark:text-red-400">
                <ShieldX className="h-5 w-5" />
                <strong>INTERACTION CONTRE-INDIQUEE DETECTEE</strong>
              </div>
            )}
            {checkResult.has_major && !checkResult.has_contraindicated && (
              <div className="flex items-center gap-2 rounded-lg bg-orange-50 p-3 text-sm text-orange-800 dark:bg-orange-900/20 dark:text-orange-400">
                <AlertTriangle className="h-5 w-5" />
                <strong>Interaction majeure detectee</strong>
              </div>
            )}
            {checkResult.interactions.length === 0 && (
              <div className="flex items-center gap-2 rounded-lg bg-green-50 p-3 text-sm text-green-800 dark:bg-green-900/20 dark:text-green-400">
                <ShieldCheck className="h-5 w-5" />
                Aucune interaction detectee
              </div>
            )}
            {checkResult.allergy_warnings.map((warning, i) => (
              <div key={i} className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-800 dark:bg-red-900/20 dark:text-red-400">
                <AlertTriangle className="h-4 w-4" />
                {warning}
              </div>
            ))}
            {checkResult.interactions.map((inter, i) => (
              <div key={i} className="rounded-lg border border-[var(--color-border-primary)] p-3">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-[var(--color-text-primary)]">
                    {inter.medication_a_name} + {inter.medication_b_name}
                  </p>
                  <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${severityConfig[inter.severity]?.color || ''}`}>
                    {severityConfig[inter.severity]?.label || inter.severity}
                  </span>
                </div>
                <p className="mt-1 text-sm text-[var(--color-text-secondary)]">{inter.clinical_effect}</p>
                <p className="mt-1 text-xs text-brand-600 dark:text-brand-400">{inter.recommendation}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Interactions Database */}
      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-[var(--color-text-primary)]">
          Base de donnees des interactions
        </h2>
        {loading ? (
          <div className="flex justify-center py-8">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600" />
          </div>
        ) : interactions.length === 0 ? (
          <p className="text-sm text-[var(--color-text-tertiary)]">
            Aucune interaction enregistree
          </p>
        ) : (
          <div className="space-y-3">
            {interactions.map((inter) => {
              const config = severityConfig[inter.severity];
              return (
                <div
                  key={inter.id}
                  className="flex items-start gap-4 rounded-lg border border-[var(--color-border-primary)] p-4 transition-colors hover:bg-[var(--color-bg-secondary)]"
                >
                  <div className={`rounded-lg p-2 ${config?.color || ''}`}>
                    {config?.icon && <config.icon className="h-5 w-5" />}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-semibold text-[var(--color-text-primary)]">
                        {inter.medication_a_name} + {inter.medication_b_name}
                      </p>
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${config?.color || ''}`}>
                        {config?.label || inter.severity}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-[var(--color-text-secondary)]">
                      {inter.clinical_effect}
                    </p>
                    {inter.mechanism && (
                      <p className="mt-1 text-xs text-[var(--color-text-tertiary)]">
                        Mecanisme: {inter.mechanism}
                      </p>
                    )}
                    <p className="mt-2 text-xs font-medium text-brand-600 dark:text-brand-400">
                      {inter.recommendation}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
