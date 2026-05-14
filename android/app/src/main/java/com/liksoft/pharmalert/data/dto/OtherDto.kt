package com.liksoft.pharmalert.data.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class AdministrationResponse(
    val id: Int,
    @SerialName("prescription_id") val prescriptionId: Int,
    @SerialName("patient_ipp") val patientIpp: String,
    @SerialName("scheduled_at") val scheduledAt: String,
    @SerialName("administered_at") val administeredAt: String? = null,
    @SerialName("dose_given") val doseGiven: Double? = null,
    val status: String,
    val notes: String? = null,
    @SerialName("medication_name") val medicationName: String? = null,
    @SerialName("patient_name") val patientName: String? = null
)

@Serializable
data class AdministrationListResponse(
    val administrations: List<AdministrationResponse>,
    val total: Int
)

@Serializable
data class RecordAdministrationRequest(
    val status: String,
    @SerialName("dose_given") val doseGiven: Double? = null,
    val notes: String? = null
)

@Serializable
data class PatientAllergyResponse(
    val id: Int,
    @SerialName("patient_ipp") val patientIpp: String,
    @SerialName("allergen_type") val allergenType: String,
    @SerialName("allergen_name") val allergenName: String,
    @SerialName("atc_code") val atcCode: String? = null,
    val severity: String,
    @SerialName("reaction_type") val reactionType: String,
    val confirmed: Boolean
)

@Serializable
data class AllergyListResponse(
    val allergies: List<PatientAllergyResponse>,
    val total: Int
)

@Serializable
data class DashboardResponse(
    val stats: DashboardStats,
    val alerts: DashboardAlerts
)

@Serializable
data class DashboardStats(
    @SerialName("pending_validations") val pendingValidations: Int,
    @SerialName("critical_interactions") val criticalInteractions: Int,
    @SerialName("missed_doses_today") val missedDosesToday: Int,
    @SerialName("compliance_rate") val complianceRate: Double,
    @SerialName("total_active_prescriptions") val totalActivePrescriptions: Int,
    @SerialName("total_patients") val totalPatients: Int
)

@Serializable
data class DashboardAlerts(
    @SerialName("critical_interactions") val criticalInteractions: List<AlertItem>,
    @SerialName("recent_adverse_events") val recentAdverseEvents: List<AlertItem>
)

@Serializable
data class AlertItem(
    val id: Int,
    val message: String? = null,
    val severity: String? = null
)

@Serializable
data class AuditLogResponse(
    val id: Int,
    val action: String,
    @SerialName("entity_type") val entityType: String,
    @SerialName("entity_id") val entityId: Int? = null,
    @SerialName("user_id") val userId: Int? = null,
    @SerialName("user_name") val userName: String? = null,
    val details: String? = null,
    @SerialName("ip_address") val ipAddress: String? = null,
    @SerialName("created_at") val createdAt: String
)

@Serializable
data class AuditLogListResponse(
    val logs: List<AuditLogResponse>,
    val total: Int
)
