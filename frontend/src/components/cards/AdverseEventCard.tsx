import React from 'react';
import { Bug } from 'lucide-react';
import type { AdverseEvent } from '../../types';
import { getSeverityColor } from '../../utils';

interface AdverseEventCardProps {
  event: AdverseEvent;
  onClick?: () => void;
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

export function AdverseEventCard({ event, onClick }: AdverseEventCardProps) {
  return (
    <div className="card cursor-pointer transition-shadow hover:shadow-md" onClick={onClick}>
      <div className="flex items-start gap-3">
        <div className={`rounded-lg p-2 ${getSeverityColor(event.severity)}`}>
          <Bug className="h-5 w-5" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-[var(--color-text-primary)]">
              {eventTypeLabels[event.event_type] || event.event_type}
            </h3>
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${getSeverityColor(event.severity)}`}>
              {event.severity}
            </span>
          </div>
          <p className="mt-1 text-xs text-[var(--color-text-secondary)]">
            Patient: {event.patient_ipp}
            {event.medication_name && ` | ${event.medication_name}`}
          </p>
          <p className="mt-1 text-sm text-[var(--color-text-primary)]">
            {event.description}
          </p>
          <div className="mt-2 flex items-center justify-between">
            <span className="text-xs text-[var(--color-text-tertiary)]">
              {statusLabels[event.status] || event.status}
            </span>
            <span className="text-xs text-[var(--color-text-tertiary)]">
              {new Date(event.reported_at).toLocaleDateString('fr-FR')}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
