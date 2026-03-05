import type {
  InteractionSeverity,
  PrescriptionStatus,
  ValidationStatus,
  AdministrationStatus,
  AllergySeverity,
  AdverseEventSeverity,
} from '../types';

/**
 * PharmAlert brand color palette (Blue #3B82F6).
 */
export const colors = {
  brand: {
    50: '#EFF6FF',
    100: '#DBEAFE',
    200: '#BFDBFE',
    300: '#93C5FD',
    400: '#60A5FA',
    500: '#3B82F6',
    600: '#2563EB',
    700: '#1D4ED8',
    800: '#1E40AF',
    900: '#1E3A8A',
    950: '#172554',
  },
} as const;

/**
 * Get CSS class for interaction severity.
 */
export function getSeverityColor(severity: InteractionSeverity | AllergySeverity | AdverseEventSeverity | string): string {
  const map: Record<string, string> = {
    minor: 'severity-minor',
    mild: 'severity-minor',
    moderate: 'severity-moderate',
    major: 'severity-major',
    serious: 'severity-major',
    contraindicated: 'severity-contraindicated',
    severe: 'severity-contraindicated',
    life_threatening: 'severity-contraindicated',
  };
  return map[severity] || '';
}

/**
 * Get CSS class for prescription/administration status.
 */
export function getStatusColor(status: PrescriptionStatus | ValidationStatus | AdministrationStatus | string): string {
  const map: Record<string, string> = {
    active: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    completed: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400',
    suspended: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
    cancelled: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    pending: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
    validated: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    rejected: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    given: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    refused: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    missed: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
    delayed: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
  };
  return map[status] || '';
}
