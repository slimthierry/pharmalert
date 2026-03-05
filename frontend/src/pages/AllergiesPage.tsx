import { useState, useEffect } from 'react';
import { Search, Plus, ShieldAlert, Trash2, Edit } from 'lucide-react';

interface Allergy {
  id: number;
  patient_ipp: string;
  allergen_type: string;
  allergen_name: string;
  atc_code: string | null;
  severity: string;
  reaction_type: string;
  confirmed: boolean;
  created_at: string;
}

const severityLabels: Record<string, string> = {
  mild: 'Legere',
  moderate: 'Moderee',
  severe: 'Severe',
  life_threatening: 'Menace vitale',
};

const allergenTypeLabels: Record<string, string> = {
  medication: 'Medicament',
  food: 'Alimentaire',
  environmental: 'Environnemental',
};

export default function AllergiesPage() {
  const [allergies, setAllergies] = useState<Allergy[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchIpp, setSearchIpp] = useState('');

  const fetchAllergies = async (ipp?: string) => {
    try {
      const token = localStorage.getItem('pharmalert-token');
      const params = new URLSearchParams();
      if (ipp) params.set('patient_ipp', ipp);
      const response = await fetch(`/api/v1/allergies/?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setAllergies(data.allergies);
      }
    } catch {
      // Handle error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllergies();
  }, []);

  const handleSearch = () => {
    setLoading(true);
    fetchAllergies(searchIpp);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">
            Allergies patients
          </h1>
          <p className="text-sm text-[var(--color-text-secondary)]">
            Gestion des allergies medicamenteuses, alimentaires et environnementales
          </p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Declarer une allergie
        </button>
      </div>

      {/* Search by IPP */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
          <input
            type="text"
            placeholder="Rechercher par IPP patient..."
            value={searchIpp}
            onChange={(e) => setSearchIpp(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            className="input-field pl-10"
          />
        </div>
        <button onClick={handleSearch} className="btn-secondary">
          Rechercher
        </button>
      </div>

      {/* Allergies List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600" />
        </div>
      ) : allergies.length === 0 ? (
        <div className="card text-center">
          <ShieldAlert className="mx-auto mb-3 h-12 w-12 text-[var(--color-text-tertiary)]" />
          <p className="text-sm text-[var(--color-text-tertiary)]">
            Aucune allergie enregistree{searchIpp ? ` pour le patient ${searchIpp}` : ''}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {allergies.map((allergy) => (
            <div key={allergy.id} className="card">
              <div className="mb-3 flex items-start justify-between">
                <div>
                  <p className="text-sm font-semibold text-[var(--color-text-primary)]">
                    {allergy.allergen_name}
                  </p>
                  <p className="text-xs text-[var(--color-text-tertiary)]">
                    Patient: {allergy.patient_ipp}
                  </p>
                </div>
                <span
                  className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
                    allergy.severity === 'life_threatening'
                      ? 'severity-contraindicated'
                      : allergy.severity === 'severe'
                        ? 'severity-major'
                        : allergy.severity === 'moderate'
                          ? 'severity-moderate'
                          : 'severity-minor'
                  }`}
                >
                  {severityLabels[allergy.severity] || allergy.severity}
                </span>
              </div>

              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-[var(--color-text-tertiary)]">Type</span>
                  <span className="text-[var(--color-text-secondary)]">
                    {allergenTypeLabels[allergy.allergen_type] || allergy.allergen_type}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-[var(--color-text-tertiary)]">Reaction</span>
                  <span className="text-[var(--color-text-secondary)]">{allergy.reaction_type}</span>
                </div>
                {allergy.atc_code && (
                  <div className="flex justify-between text-xs">
                    <span className="text-[var(--color-text-tertiary)]">Code ATC</span>
                    <span className="font-mono text-[var(--color-text-secondary)]">{allergy.atc_code}</span>
                  </div>
                )}
                <div className="flex justify-between text-xs">
                  <span className="text-[var(--color-text-tertiary)]">Confirmee</span>
                  <span className={allergy.confirmed ? 'text-green-600 dark:text-green-400' : 'text-amber-600 dark:text-amber-400'}>
                    {allergy.confirmed ? 'Oui' : 'Non confirmee'}
                  </span>
                </div>
              </div>

              <div className="mt-4 flex justify-end gap-2">
                <button className="rounded p-1.5 text-[var(--color-text-tertiary)] transition-colors hover:bg-[var(--color-bg-tertiary)] hover:text-[var(--color-text-primary)]">
                  <Edit className="h-4 w-4" />
                </button>
                <button className="rounded p-1.5 text-[var(--color-text-tertiary)] transition-colors hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
