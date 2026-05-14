package com.liksoft.pharmalert.data.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class MedicationResponse(
    val id: Int,
    val name: String,
    @SerialName("atc_code") val atcCode: String? = null,
    val form: String? = null,
    val dosage: String? = null,
    @SerialName("active_principle") val activePrinciple: String? = null,
    val manufacturer: String? = null,
    @SerialName("is_controlled") val isControlled: Boolean = false
)

@Serializable
data class MedicationListResponse(
    val medications: List<MedicationResponse>,
    val total: Int
)
