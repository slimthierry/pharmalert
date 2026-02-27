import React from 'react';
import { Pill } from 'lucide-react';
import type { Medication } from '@pharmalert/types';

interface DrugCardProps {
  medication: Medication;
  onClick?: () => void;
}

const formLabels: Record<string, string> = {
  tablet: 'Comprime',
  capsule: 'Gelule',
  injection: 'Injection',
  syrup: 'Sirop',
  cream: 'Creme',
  patch: 'Patch',
};

export function DrugCard({ medication, onClick }: DrugCardProps) {
  return (
    <div
      className="card cursor-pointer transition-shadow hover:shadow-md"
      onClick={onClick}
    >
      <div className="flex items-start gap-3">
        <div className="rounded-lg bg-brand-100 p-2 dark:bg-brand-900/30">
          <Pill className="h-5 w-5 text-brand-600 dark:text-brand-400" />
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-[var(--color-text-primary)]">
            {medication.name}
          </h3>
          <p className="text-xs text-[var(--color-text-secondary)]">
            DCI: {medication.dci}
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            {medication.atc_code && (
              <span className="rounded bg-[var(--color-bg-tertiary)] px-1.5 py-0.5 font-mono text-xs text-[var(--color-text-secondary)]">
                {medication.atc_code}
              </span>
            )}
            <span className="rounded bg-brand-50 px-1.5 py-0.5 text-xs text-brand-700 dark:bg-brand-950 dark:text-brand-400">
              {formLabels[medication.form] || medication.form}
            </span>
            <span className="text-xs text-[var(--color-text-tertiary)]">
              {medication.dosage_unit}
            </span>
          </div>
          {medication.manufacturer && (
            <p className="mt-1 text-xs text-[var(--color-text-tertiary)]">
              {medication.manufacturer}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
