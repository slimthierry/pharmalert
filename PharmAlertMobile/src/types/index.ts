// ========================
// Enums
// ========================

export enum UserRole {
  ADMIN = 'admin',
  MEDECIN = 'medecin',
  PHARMACIEN = 'pharmacien',
  INFIRMIER = 'infirmier',
  PREPARATEUR = 'preparateur',
}

export enum MedicationForm {
  TABLET = 'tablet',
  CAPSULE = 'capsule',
  INJECTION = 'injection',
  SYRUP = 'syrup',
  CREAM = 'cream',
  PATCH = 'patch',
}

export enum InteractionSeverity {
  MINOR = 'minor',
  MODERATE = 'moderate',
  MAJOR = 'major',
  CONTRAINDICATED = 'contraindicated',
}

export enum PrescriptionStatus {
  ACTIVE = 'active',
  COMPLETED = 'completed',
  SUSPENDED = 'suspended',
  CANCELLED = 'cancelled',
}

export enum ValidationStatus {
  PENDING = 'pending',
  VALIDATED = 'validated',
  REJECTED = 'rejected',
}

export enum AdministrationRoute {
  ORAL = 'oral',
  IV = 'iv',
  IM = 'im',
  SC = 'sc',
  TOPICAL = 'topical',
  INHALED = 'inhaled',
}

export enum AdministrationStatus {
  GIVEN = 'given',
  REFUSED = 'refused',
  MISSED = 'missed',
  DELAYED = 'delayed',
}

export enum AllergenType {
  MEDICATION = 'medication',
  FOOD = 'food',
  ENVIRONMENTAL = 'environmental',
}

export enum AllergySeverity {
  MILD = 'mild',
  MODERATE = 'moderate',
  SEVERE = 'severe',
  LIFE_THREATENING = 'life_threatening',
}

export enum ReactionType {
  RASH = 'rash',
  ANAPHYLAXIS = 'anaphylaxis',
  NAUSEA = 'nausea',
  RESPIRATORY = 'respiratory',
  OTHER = 'other',
}

// ========================
// Core interfaces
// ========================

export interface User {
  id: number;
  email: string;
  name: string;
  role: UserRole;
  service?: string;
  rpps_number?: string;
  created_at: string;
}

export interface Medication {
  id: number;
  name: string;
  dci?: string;
  atc_code?: string;
  form: MedicationForm;
  dosage_unit: string;
  manufacturer?: string;
  contraindications: string[];
  side_effects: string[];
  created_at: string;
}

export interface Interaction {
  id: number;
  medication_a_id: number;
  medication_a_name?: string;
  medication_b_id: number;
  medication_b_name?: string;
  severity: InteractionSeverity;
  mechanism?: string;
  clinical_effect: string;
  recommendation: string;
  source?: string;
  created_at: string;
}

export interface Prescription {
  id: number;
  patient_ipp: string;
  patient_name?: string;
  prescriber_id?: number;
  prescriber_name?: string;
  medication_id?: number;
  medication_name?: string;
  dosage_value: number;
  dosage_unit: string;
  frequency: string;
  route: AdministrationRoute;
  start_date: string;
  end_date?: string;
  status: PrescriptionStatus;
  validation_status: ValidationStatus;
  validated_by?: number;
  validator_name?: string;
  validation_notes?: string;
  interactions_checked: boolean;
  override_justification?: string;
  created_at: string;
}

export interface Administration {
  id: number;
  prescription_id: number;
  nurse_id?: number;
  nurse_name?: string;
  scheduled_at: string;
  administered_at?: string;
  dose_given?: number;
  status: AdministrationStatus;
  patient_ipp: string;
  patient_name?: string;
  medication_name?: string;
  notes?: string;
  created_at: string;
}

export interface PatientAllergy {
  id: number;
  patient_ipp: string;
  allergen_type: AllergenType;
  allergen_name: string;
  atc_code?: string;
  severity: AllergySeverity;
  reaction_type: ReactionType;
  confirmed: boolean;
  reported_by?: number;
  created_at: string;
}

export interface AdverseEvent {
  id: number;
  patient_ipp: string;
  medication_id?: number;
  medication_name?: string;
  prescription_id?: number;
  event_type: string;
  severity: string;
  description: string;
  outcome?: string;
  reported_by: number;
  reported_by_name?: string;
  reported_at: string;
  status: string;
  created_at: string;
}

export interface AuditLog {
  id: number;
  user_id?: number;
  user_name?: string;
  action: string;
  entity_type: string;
  entity_id?: string;
  details?: Record<string, unknown>;
  ip_address?: string;
  timestamp: string;
}

export interface EntityBrief {
  id: number;
  name: string;
  code: string;
  logo_url?: string;
  is_active: boolean;
}

export interface DashboardStats {
  pending_validations: number;
  critical_interactions: number;
  missed_doses_today: number;
  compliance_rate: number;
  total_active_prescriptions: number;
  total_patients: number;
}

export interface DashboardResponse {
  stats: DashboardStats;
  alerts: {
    critical_interactions: Interaction[];
    recent_adverse_events: AdverseEvent[];
  };
}

export interface InteractionCheckResponse {
  interactions: Array<{
    medication_a_id: number;
    medication_a_name: string;
    medication_b_id: number;
    medication_b_name: string;
    severity: InteractionSeverity;
    clinical_effect: string;
    recommendation: string;
  }>;
  has_contraindicated: boolean;
  has_major: boolean;
  allergy_warnings: string[];
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  role: string;
  name: string;
}

export interface SIHStatus {
  connected: boolean;
  last_sync: string | null;
  patients_count: number;
  drugs_count: number;
  orders_count: number;
  error: string | null;
}
