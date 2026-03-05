import React from 'react';
import { Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import type { Administration, AdministrationStatus } from '../../types';

interface DoseScheduleProps {
  administrations: Administration[];
  onRecord?: (id: number, status: AdministrationStatus) => void;
}

const statusConfig: Record<string, { icon: React.ElementType; color: string; label: string }> = {
  given: { icon: CheckCircle, color: 'text-green-500', label: 'Administre' },
  refused: { icon: XCircle, color: 'text-red-500', label: 'Refuse' },
  missed: { icon: AlertCircle, color: 'text-orange-500', label: 'Manque' },
  delayed: { icon: Clock, color: 'text-amber-500', label: 'Retarde' },
};

export function DoseSchedule({ administrations, onRecord }: DoseScheduleProps) {
  const formatTime = (dateStr: string) => {
    return new Date(dateStr).toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-2">
      {administrations.map((admin) => {
        const config = statusConfig[admin.status] || statusConfig.missed;
        const Icon = config.icon;

        return (
          <div
            key={admin.id}
            className="flex items-center gap-3 rounded-lg border border-[var(--color-border-primary)] p-3"
          >
            <div className="w-14 text-center">
              <span className="text-sm font-bold text-[var(--color-text-primary)]">
                {formatTime(admin.scheduled_at)}
              </span>
            </div>
            <Icon className={`h-5 w-5 ${config.color}`} />
            <div className="flex-1">
              <p className="text-sm font-medium text-[var(--color-text-primary)]">
                {admin.medication_name || 'Medicament'}
              </p>
              <p className="text-xs text-[var(--color-text-tertiary)]">
                {admin.patient_name || admin.patient_ipp}
                {admin.dose_given && ` - ${admin.dose_given} mg`}
              </p>
            </div>
            <span className="text-xs font-medium text-[var(--color-text-secondary)]">
              {config.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}
