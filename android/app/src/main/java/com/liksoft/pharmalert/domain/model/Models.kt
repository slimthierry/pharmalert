package com.liksoft.pharmalert.domain.model

data class User(
    val id: Int,
    val email: String,
    val name: String,
    val role: UserRole,
    val service: String?
)

enum class UserRole {
    ADMIN,
    MEDECIN,
    PHARMACIEN,
    INFIRMIER,
    TECHNICIEN;

    companion object {
        fun fromString(value: String): UserRole = when (value.lowercase()) {
            "admin" -> ADMIN
            "medecin", "medecin_labo" -> MEDECIN
            "pharmacien" -> PHARMACIEN
            "infirmier" -> INFIRMIER
            "technicien_labo" -> TECHNICIEN
            else -> TECHNICIEN
        }
    }
}

data class Prescription(
    val id: Int,
    val patientIpp: String,
    val patientName: String,
    val medicationName: String,
    val dosage: String,
    val frequency: String,
    val route: String,
    val startDate: String,
    val endDate: String?,
    val status: PrescriptionStatus,
    val validationStatus: ValidationStatus,
    val interactionsChecked: Boolean
)

enum class PrescriptionStatus {
    ACTIVE, COMPLETED, SUSPENDED, CANCELLED
}

enum class ValidationStatus {
    PENDING, VALIDATED, REJECTED
}

data class Interaction(
    val medicationA: String,
    val medicationB: String,
    val severity: InteractionSeverity,
    val clinicalEffect: String,
    val recommendation: String?
)

enum class InteractionSeverity {
    MINOR, MODERATE, MAJOR, CONTRAINDICATED;

    companion object {
        fun fromString(value: String): InteractionSeverity = when (value.lowercase()) {
            "minor" -> MINOR
            "moderate" -> MODERATE
            "major" -> MAJOR
            "contraindicated", "life_threatening" -> CONTRAINDICATED
            else -> MINOR
        }
    }
}

data class Administration(
    val id: Int,
    val patientIpp: String,
    val patientName: String,
    val medicationName: String,
    val scheduledAt: String,
    val administeredAt: String?,
    val doseGiven: Double?,
    val status: AdministrationStatus,
    val notes: String?
)

enum class AdministrationStatus {
    GIVEN, REFUSED, MISSED, DELAYED, PENDING
}

data class Allergy(
    val id: Int,
    val patientIpp: String,
    val allergenName: String,
    val allergenType: String,
    val atcCode: String?,
    val severity: AllergySeverity,
    val reactionType: String,
    val confirmed: Boolean
)

enum class AllergySeverity {
    MILD, MODERATE, SEVERE, LIFE_THREATENING;

    companion object {
        fun fromString(value: String): AllergySeverity = when (value.lowercase()) {
            "mild" -> MILD
            "moderate" -> MODERATE
            "severe" -> SEVERE
            "life_threatening" -> LIFE_THREATENING
            else -> MODERATE
        }
    }
}

data class DashboardStats(
    val pendingPrescriptions: Int,
    val pendingAdministrations: Int,
    val activeInteractions: Int,
    val todayTotal: Int,
    val todayCompleted: Int,
    val todayRefused: Int
)