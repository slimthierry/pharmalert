/**
 * FHIR R4 MedicationRequest resource mapping.
 * Converts between PharmAlert Prescription and FHIR MedicationRequest.
 */

import type { Prescription } from '@pharmalert/types';

export interface FHIRMedicationRequest {
  resourceType: 'MedicationRequest';
  id?: string;
  status: string;
  intent: string;
  medicationCodeableConcept?: {
    coding?: Array<{ system?: string; code?: string; display?: string }>;
    text?: string;
  };
  subject?: { reference?: string; display?: string };
  requester?: { reference?: string; display?: string };
  dosageInstruction?: Array<{
    text?: string;
    route?: { text?: string };
  }>;
  authoredOn?: string;
}

const STATUS_MAP: Record<string, string> = {
  active: 'active',
  completed: 'completed',
  suspended: 'on-hold',
  cancelled: 'cancelled',
};

const REVERSE_STATUS_MAP: Record<string, string> = {
  active: 'active',
  completed: 'completed',
  'on-hold': 'suspended',
  cancelled: 'cancelled',
};

export function toFHIRMedicationRequest(prescription: Prescription): FHIRMedicationRequest {
  return {
    resourceType: 'MedicationRequest',
    id: String(prescription.id),
    status: STATUS_MAP[prescription.status] || 'unknown',
    intent: 'order',
    medicationCodeableConcept: {
      text: prescription.medication_name || undefined,
    },
    subject: {
      reference: `Patient/${prescription.patient_ipp}`,
      display: prescription.patient_name,
    },
    requester: {
      reference: `Practitioner/${prescription.prescriber_id}`,
      display: prescription.prescriber_name || undefined,
    },
    dosageInstruction: [
      {
        text: `${prescription.dosage_value} ${prescription.dosage_unit} ${prescription.frequency}`,
        route: { text: prescription.route },
      },
    ],
    authoredOn: prescription.created_at,
  };
}

export function fromFHIRMedicationRequest(
  fhir: FHIRMedicationRequest,
): Partial<Prescription> {
  const patientRef = fhir.subject?.reference?.split('/')[1];
  return {
    patient_ipp: patientRef || '',
    patient_name: fhir.subject?.display || '',
    status: (REVERSE_STATUS_MAP[fhir.status] || 'active') as Prescription['status'],
  };
}
