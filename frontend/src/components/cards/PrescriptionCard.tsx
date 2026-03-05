import React from 'react';
import { FileText, Check, X, Clock } from 'lucide-react';
import type { Prescription } from '../../types';
import { getStatusColor } from '../../utils';

interface PrescriptionCardProps {
  prescription: Prescription;
  onValidate?: () => void;
  onReject?: () => void;
}

const validationIcons: Record<string, React.ElementType> = {
  pending: Clock,
  validated: Check,
  rejected: X,
};

export function PrescriptionCard({
  prescription,
  onValidate,
  onReject,
}: PrescriptionCardProps) {
  const ValidationIcon = validationIcons[prescription.validation_status] || Clock;

  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className="rounded-lg bg-brand-100 p-2 dark:bg-brand-900/30">
            <FileText className="h-5 w-5 text-brand-600 dark:text-brand-400" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-[var(--color-text-primary)]">
              {prescription.medication_name || `Medicament #${prescription.medication_id}`}
            </h3>
            <p className="text-xs text-[var(--color-text-secondary)]">
              {prescription.patient_name} ({prescription.patient_ipp})
            </p>
            <p className="mt-1 text-xs text-[var(--color-text-tertiary)]">
              {prescription.dosage_value} {prescription.dosage_unit} - {prescription.frequency} - voie {prescription.route}
            </p>
            <p className="text-xs text-[var(--color-text-tertiary)]">
              Prescrit par {prescription.prescriber_name || 'inconnu'} le{' '}
              {new Date(prescription.created_at).toLocaleDateString('fr-FR')}
            </p>
          </div>
        </div>
        <div className="flex flex-col items-end gap-1">
          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${getStatusColor(prescription.status)}`}>
            {prescription.status}
          </span>
          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${getStatusColor(prescription.validation_status)}`}>
            <ValidationIcon className="mr-1 inline h-3 w-3" />
            {prescription.validation_status}
          </span>
        </div>
      </div>

      {prescription.validation_status === 'pending' && (onValidate || onReject) && (
        <div className="mt-3 flex justify-end gap-2 border-t border-[var(--color-border-primary)] pt-3">
          {onReject && (
            <button
              onClick={onReject}
              className="rounded-lg border border-red-200 px-3 py-1.5 text-xs font-medium text-red-600 transition-colors hover:bg-red-50 dark:border-red-800 dark:text-red-400 dark:hover:bg-red-900/20"
            >
              Rejeter
            </button>
          )}
          {onValidate && (
            <button
              onClick={onValidate}
              className="rounded-lg bg-green-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-green-700"
            >
              Valider
            </button>
          )}
        </div>
      )}
    </div>
  );
}
