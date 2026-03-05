import { useState, useEffect } from 'react';
import { Plus, Search, Check, X, AlertTriangle } from 'lucide-react';

interface Prescription {
  id: number;
  patient_ipp: string;
  patient_name: string;
  prescriber_name: string | null;
  medication_name: string | null;
  dosage_value: number;
  dosage_unit: string;
  frequency: string;
  route: string;
  start_date: string;
  end_date: string | null;
  status: string;
  validation_status: string;
  validator_name: string | null;
  interactions_checked: boolean;
  created_at: string;
}

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  completed: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400',
  suspended: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
  cancelled: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
};

const validationColors: Record<string, string> = {
  pending: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
  validated: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  rejected: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
};

export default function PrescriptionsPage() {
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showCreate, setShowCreate] = useState(false);

  const fetchPrescriptions = async () => {
    try {
      const token = localStorage.getItem('pharmalert-token');
      const params = new URLSearchParams();
      if (search) params.set('patient_ipp', search);
      const response = await fetch(`/api/v1/prescriptions/?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setPrescriptions(data.prescriptions);
      }
    } catch {
      // Handle error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrescriptions();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">
            Prescriptions
          </h1>
          <p className="text-sm text-[var(--color-text-secondary)]">
            Gestion des ordonnances avec verification d'interactions en temps reel
          </p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          Nouvelle prescription
        </button>
      </div>

      {/* Search */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
          <input
            type="text"
            placeholder="Rechercher par IPP patient..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && fetchPrescriptions()}
            className="input-field pl-10"
          />
        </div>
        <button onClick={fetchPrescriptions} className="btn-secondary">
          Rechercher
        </button>
      </div>

      {/* Create Form */}
      {showCreate && (
        <div className="card border-brand-200 dark:border-brand-800">
          <h3 className="mb-4 text-lg font-semibold text-[var(--color-text-primary)]">
            Nouvelle prescription
          </h3>
          <div className="mb-4 flex items-center gap-2 rounded-lg bg-amber-50 p-3 text-sm text-amber-800 dark:bg-amber-900/20 dark:text-amber-400">
            <AlertTriangle className="h-4 w-4" />
            Les interactions seront verifiees automatiquement lors de la creation.
          </div>
          <form className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-[var(--color-text-primary)]">IPP Patient</label>
              <input type="text" className="input-field" placeholder="IPP001" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-[var(--color-text-primary)]">Nom du patient</label>
              <input type="text" className="input-field" placeholder="Jean Dupont" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-[var(--color-text-primary)]">Medicament</label>
              <select className="input-field">
                <option value="">Selectionner un medicament</option>
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-[var(--color-text-primary)]">Posologie</label>
              <div className="flex gap-2">
                <input type="number" className="input-field" placeholder="20" />
                <select className="input-field w-24">
                  <option>mg</option>
                  <option>g</option>
                  <option>ml</option>
                  <option>UI</option>
                </select>
              </div>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-[var(--color-text-primary)]">Frequence</label>
              <input type="text" className="input-field" placeholder="3x/day" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-[var(--color-text-primary)]">Voie d'administration</label>
              <select className="input-field">
                <option value="oral">Orale</option>
                <option value="iv">Intraveineuse</option>
                <option value="im">Intramusculaire</option>
                <option value="sc">Sous-cutanee</option>
                <option value="topical">Topique</option>
                <option value="inhaled">Inhalee</option>
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-[var(--color-text-primary)]">Date de debut</label>
              <input type="date" className="input-field" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-[var(--color-text-primary)]">Date de fin</label>
              <input type="date" className="input-field" />
            </div>
            <div className="col-span-2 flex justify-end gap-3">
              <button type="button" onClick={() => setShowCreate(false)} className="btn-secondary">
                Annuler
              </button>
              <button type="submit" className="btn-primary">
                Creer la prescription
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Prescriptions List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600" />
        </div>
      ) : (
        <div className="card overflow-hidden p-0">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[var(--color-border-primary)] bg-[var(--color-bg-secondary)]">
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-[var(--color-text-secondary)]">Patient</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-[var(--color-text-secondary)]">Medicament</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-[var(--color-text-secondary)]">Posologie</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-[var(--color-text-secondary)]">Prescripteur</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-[var(--color-text-secondary)]">Statut</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-[var(--color-text-secondary)]">Validation</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-[var(--color-text-secondary)]">Interactions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-border-primary)]">
              {prescriptions.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-sm text-[var(--color-text-tertiary)]">
                    Aucune prescription trouvee
                  </td>
                </tr>
              ) : (
                prescriptions.map((rx) => (
                  <tr key={rx.id} className="hover:bg-[var(--color-bg-secondary)] transition-colors">
                    <td className="px-4 py-3">
                      <p className="text-sm font-medium text-[var(--color-text-primary)]">{rx.patient_name}</p>
                      <p className="text-xs text-[var(--color-text-tertiary)]">{rx.patient_ipp}</p>
                    </td>
                    <td className="px-4 py-3 text-sm text-[var(--color-text-primary)]">{rx.medication_name}</td>
                    <td className="px-4 py-3 text-sm text-[var(--color-text-primary)]">
                      {rx.dosage_value} {rx.dosage_unit} - {rx.frequency}
                    </td>
                    <td className="px-4 py-3 text-sm text-[var(--color-text-secondary)]">{rx.prescriber_name}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${statusColors[rx.status] || ''}`}>
                        {rx.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${validationColors[rx.validation_status] || ''}`}>
                        {rx.validation_status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {rx.interactions_checked ? (
                        <Check className="h-4 w-4 text-green-500" />
                      ) : (
                        <X className="h-4 w-4 text-red-500" />
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
