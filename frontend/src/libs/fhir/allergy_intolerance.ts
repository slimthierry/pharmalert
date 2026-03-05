/**
 * FHIR R4 AllergyIntolerance resource mapping.
 * Converts between PharmAlert PatientAllergy and FHIR AllergyIntolerance.
 */

import type { PatientAllergy } from '../../types';

export interface FHIRAllergyIntolerance {
  resourceType: 'AllergyIntolerance';
  id?: string;
  clinicalStatus?: { coding?: Array<{ code?: string }> };
  verificationStatus?: { coding?: Array<{ code?: string }> };
  type?: string;
  category?: string[];
  criticality?: string;
  code?: { coding?: Array<{ system?: string; code?: string; display?: string }>; text?: string };
  patient?: { reference?: string };
  reaction?: Array<{
    manifestation?: Array<{ text?: string }>;
    severity?: string;
  }>;
  recordedDate?: string;
}

const CATEGORY_MAP: Record<string, string> = {
  medication: 'medication',
  food: 'food',
  environmental: 'environment',
};

const CRITICALITY_MAP: Record<string, string> = {
  mild: 'low',
  moderate: 'low',
  severe: 'high',
  life_threatening: 'high',
};

const SEVERITY_MAP: Record<string, string> = {
  mild: 'mild',
  moderate: 'moderate',
  severe: 'severe',
  life_threatening: 'severe',
};

export function toFHIRAllergyIntolerance(allergy: PatientAllergy): FHIRAllergyIntolerance {
  const result: FHIRAllergyIntolerance = {
    resourceType: 'AllergyIntolerance',
    id: String(allergy.id),
    clinicalStatus: {
      coding: [{ code: allergy.confirmed ? 'active' : 'unconfirmed' }],
    },
    verificationStatus: {
      coding: [{ code: allergy.confirmed ? 'confirmed' : 'unconfirmed' }],
    },
    type: 'allergy',
    category: [CATEGORY_MAP[allergy.allergen_type] || 'medication'],
    criticality: CRITICALITY_MAP[allergy.severity] || 'low',
    code: {
      text: allergy.allergen_name,
    },
    patient: {
      reference: `Patient/${allergy.patient_ipp}`,
    },
    reaction: [
      {
        manifestation: [{ text: allergy.reaction_type }],
        severity: SEVERITY_MAP[allergy.severity] || 'moderate',
      },
    ],
    recordedDate: allergy.created_at,
  };

  if (allergy.atc_code) {
    result.code!.coding = [
      {
        system: 'http://www.whocc.no/atc',
        code: allergy.atc_code,
        display: allergy.allergen_name,
      },
    ];
  }

  return result;
}

export function fromFHIRAllergyIntolerance(
  fhir: FHIRAllergyIntolerance,
): Partial<PatientAllergy> {
  const patientRef = fhir.patient?.reference?.split('/')[1];
  const reverseCategory: Record<string, string> = {
    medication: 'medication',
    food: 'food',
    environment: 'environmental',
  };

  return {
    patient_ipp: patientRef || '',
    allergen_name: fhir.code?.text || '',
    allergen_type: (reverseCategory[fhir.category?.[0] || ''] || 'medication') as PatientAllergy['allergen_type'],
    atc_code: fhir.code?.coding?.[0]?.code,
    confirmed: fhir.verificationStatus?.coding?.[0]?.code === 'confirmed',
  };
}
