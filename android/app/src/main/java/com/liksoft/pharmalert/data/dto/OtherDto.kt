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
    @SerialName("pending_prescriptions") val pendingPrescriptions: Int,
    @SerialName("pending_administrations") val pendingAdministrations: Int,
    @SerialName("active_interactions") val activeInteractions: Int,
    @SerialName("today_administrations") val todayAdministrations: Int,
    @SerialName("completed_administrations") val completedAdministrations: Int,
    @SerialName("refused_administrations") val refusedAdministrations: Int,
    @SerialName("pending_interactions") val pendingInteractions: Int? = null,
    @SerialName("total_prescriptions") val totalPrescriptions: Int? = null,
    @SerialName("total_adverse_events") val totalAdverseEvents: Int? = null
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
