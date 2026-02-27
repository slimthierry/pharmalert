import React from 'react';
import { AlertTriangle, ShieldX, ShieldAlert, ShieldCheck } from 'lucide-react';
import type { InteractionCheckResult, InteractionSeverity } from '@pharmalert/types';
import { getSeverityColor } from '@pharmalert/utils';

interface InteractionAlertProps {
  interaction: InteractionCheckResult;
}

const severityIcons: Record<string, React.ElementType> = {
  minor: ShieldCheck,
  moderate: ShieldAlert,
  major: AlertTriangle,
  contraindicated: ShieldX,
};

const severityLabels: Record<string, string> = {
  minor: 'Mineure',
  moderate: 'Moderee',
  major: 'Majeure',
  contraindicated: 'Contre-indiquee',
};

export function InteractionAlert({ interaction }: InteractionAlertProps) {
  const Icon = severityIcons[interaction.severity] || AlertTriangle;
  const colorClass = getSeverityColor(interaction.severity);
  const label = severityLabels[interaction.severity] || interaction.severity;

  return (
    <div className={`rounded-lg border p-4 ${
      interaction.severity === 'contraindicated'
        ? 'border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-900/20'
        : interaction.severity === 'major'
          ? 'border-orange-300 bg-orange-50 dark:border-orange-800 dark:bg-orange-900/20'
          : 'border-[var(--color-border-primary)] bg-[var(--color-bg-primary)]'
    }`}>
      <div className="flex items-start gap-3">
        <div className={`rounded-lg p-2 ${colorClass}`}>
          <Icon className="h-5 w-5" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-[var(--color-text-primary)]">
              {interaction.medication_a_name} + {interaction.medication_b_name}
            </span>
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${colorClass}`}>
              {label}
            </span>
          </div>
          <p className="mt-1 text-sm text-[var(--color-text-secondary)]">
            {interaction.clinical_effect}
          </p>
          <p className="mt-1 text-xs font-medium text-brand-600 dark:text-brand-400">
            {interaction.recommendation}
          </p>
        </div>
      </div>
    </div>
  );
}
