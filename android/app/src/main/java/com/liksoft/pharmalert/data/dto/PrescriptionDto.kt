package com.liksoft.pharmalert.data.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class PrescriptionResponse(
    val id: Int,
    @SerialName("patient_ipp") val patientIpp: String,
    @SerialName("patient_name") val patientName: String,
    @SerialName("medication_id") val medicationId: Int,
    @SerialName("medication") val medication: MedicationResponse? = null,
    @SerialName("medication_name") val medicationName: String? = null,
    @SerialName("dosage_value") val dosageValue: Double,
    @SerialName("dosage_unit") val dosageUnit: String,
    val frequency: String,
    val route: String,
    @SerialName("start_date") val startDate: String,
    @SerialName("end_date") val endDate: String? = null,
    val status: String,
    @SerialName("validation_status") val validationStatus: String,
    @SerialName("doctor_name") val doctorName: String? = null,
    @SerialName("interactions_checked") val interactionsChecked: Boolean = false
)

@Serializable
data class PrescriptionListResponse(
    val prescriptions: List<PrescriptionResponse>,
    val total: Int
)

@Serializable
data class CreatePrescriptionRequest(
    @SerialName("patient_ipp") val patientIpp: String,
    @SerialName("patient_name") val patientName: String,
    @SerialName("medication_id") val medicationId: Int,
    @SerialName("dosage_value") val dosageValue: Double,
    @SerialName("dosage_unit") val dosageUnit: String,
    val frequency: String,
    val route: String,
    @SerialName("start_date") val startDate: String,
    @SerialName("end_date") val endDate: String? = null
)

@Serializable
data class CreatePrescriptionResponse(
    val prescription: PrescriptionResponse,
    val interactions: List<InteractionCheckResult> = emptyList(),
    @SerialName("allergy_warnings") val allergyWarnings: List<String> = emptyList()
)
