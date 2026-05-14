package com.liksoft.pharmalert.data.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class InteractionCheckRequest(
    @SerialName("medication_ids") val medicationIds: List<Int>,
    @SerialName("patient_ipp") val patientIpp: String? = null
)

@Serializable
data class InteractionCheckResponse(
    val has_contraindicated: Boolean = false,
    @SerialName("has_major") val hasMajor: Boolean = false,
    @SerialName("has_moderate") val hasModerate: Boolean = false,
    @SerialName("has_minor") val hasMinor: Boolean = false,
    val interactions: List<InteractionCheckResult>
)

@Serializable
data class InteractionCheckResult(
    val id: Int? = null,
    @SerialName("medication_a_id") val medicationAId: Int,
    @SerialName("medication_b_id") val medicationBId: Int,
    @SerialName("medication_a_name") val medicationAName: String,
    @SerialName("medication_b_name") val medicationBName: String,
    val severity: String,
    @SerialName("clinical_effect") val clinicalEffect: String,
    val recommendation: String? = null,
    val source: String? = null
)

@Serializable
data class InteractionResponse(
    val id: Int,
    @SerialName("medication_a_id") val medicationAId: Int,
    @SerialName("medication_b_id") val medicationBId: Int,
    @SerialName("medication_a_name") val medicationAName: String,
    @SerialName("medication_b_name") val medicationBName: String,
    val severity: String,
    @SerialName("clinical_effect") val clinicalEffect: String,
    val recommendation: String? = null,
    val source: String? = null
)

@Serializable
data class InteractionListResponse(
    val interactions: List<InteractionResponse>,
    val total: Int
)
