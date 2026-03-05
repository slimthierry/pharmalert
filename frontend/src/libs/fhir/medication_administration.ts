/**
 * FHIR R4 MedicationAdministration resource mapping.
 * Converts between PharmAlert Administration and FHIR MedicationAdministration.
 */

import type { Administration } from '../../types';

export interface FHIRMedicationAdministration {
  resourceType: 'MedicationAdministration';
  id?: string;
  status: string;
  medicationCodeableConcept?: { text?: string };
  subject?: { reference?: string };
  performer?: Array<{ actor: { reference?: string; display?: string } }>;
  effectiveDateTime?: string;
  dosage?: { dose?: { value?: number; unit?: string } };
  request?: { reference?: string };
}

const STATUS_MAP: Record<string, string> = {
  given: 'completed',
  refused: 'not-done',
  missed: 'not-done',
  delayed: 'in-progress',
};

const REVERSE_STATUS_MAP: Record<string, string> = {
  completed: 'given',
  'not-done': 'missed',
  'in-progress': 'delayed',
};

export function toFHIRMedicationAdministration(
  admin: Administration,
): FHIRMedicationAdministration {
  const result: FHIRMedicationAdministration = {
    resourceType: 'MedicationAdministration',
    id: String(admin.id),
    status: STATUS_MAP[admin.status] || 'unknown',
    subject: {
      reference: `Patient/${admin.patient_ipp}`,
    },
    effectiveDateTime: admin.administered_at || admin.scheduled_at,
    request: {
      reference: `MedicationRequest/${admin.prescription_id}`,
    },
  };

  if (admin.medication_name) {
    result.medicationCodeableConcept = { text: admin.medication_name };
  }

  if (admin.nurse_id) {
    result.performer = [
      {
        actor: {
          reference: `Practitioner/${admin.nurse_id}`,
          display: admin.nurse_name || undefined,
        },
      },
    ];
  }

  if (admin.dose_given) {
    result.dosage = {
      dose: { value: admin.dose_given, unit: 'mg' },
    };
  }

  return result;
}

export function fromFHIRMedicationAdministration(
  fhir: FHIRMedicationAdministration,
): Partial<Administration> {
  const patientRef = fhir.subject?.reference?.split('/')[1];
  return {
    patient_ipp: patientRef || '',
    status: (REVERSE_STATUS_MAP[fhir.status] || 'missed') as Administration['status'],
    dose_given: fhir.dosage?.dose?.value,
  };
}
