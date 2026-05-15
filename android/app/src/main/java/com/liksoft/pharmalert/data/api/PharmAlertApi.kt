package com.liksoft.pharmalert.data.api

import com.liksoft.pharmalert.data.dto.*
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.request.*
import io.ktor.http.*

class PharmAlertApi(private val client: HttpClient, private val baseUrl: String) {

    private var token: String? = null

    fun setToken(t: String?) { token = t }

    private fun HttpRequestBuilder.auth() {
        token?.let { header(HttpHeaders.Authorization, "Bearer $it") }
    }

    // ========================
    // Auth
    // ========================
    suspend fun login(email: String, password: String): TokenResponse = client.post("$baseUrl/auth/login") {
        contentType(ContentType.Application.Json)
        setBody(LoginRequest(email, password))
    }.body()

    suspend fun me(): UserResponse = client.get("$baseUrl/auth/me") { auth() }.body()

    // ========================
    // Medications
    // ========================
    suspend fun getMedications(search: String? = null, skip: Int = 0, limit: Int = 50): MedicationListResponse =
        client.get("$baseUrl/medications/") {
            parameter("search", search)
            parameter("skip", skip)
            parameter("limit", limit)
            auth()
        }.body()

    suspend fun getMedication(id: Int): MedicationResponse =
        client.get("$baseUrl/medications/$id") { auth() }.body()

    // ========================
    // Prescriptions
    // ========================
    suspend fun getPrescriptions(
        patientIpp: String? = null,
        status: String? = null,
        validationStatus: String? = null
    ): PrescriptionListResponse = client.get("$baseUrl/prescriptions/") {
        parameter("patient_ipp", patientIpp)
        parameter("status", status)
        parameter("validation_status", validationStatus)
        auth()
    }.body()

    suspend fun getPrescription(id: Int): PrescriptionResponse =
        client.get("$baseUrl/prescriptions/$id") { auth() }.body()

    suspend fun createPrescription(request: CreatePrescriptionRequest): CreatePrescriptionResponse =
        client.post("$baseUrl/prescriptions/") {
            setBody(request)
            auth()
        }.body()

    // ========================
    // Interactions
    // ========================
    suspend fun checkInteractions(medicationIds: List<Int>, patientIpp: String? = null): InteractionCheckResponse =
        client.post("$baseUrl/interactions/check") {
            contentType(ContentType.Application.Json)
            setBody(InteractionCheckRequest(medicationIds, patientIpp))
            auth()
        }.body()

    suspend fun getInteractions(severity: String? = null): InteractionListResponse =
        client.get("$baseUrl/interactions/") {
            parameter("severity", severity)
            auth()
        }.body()

    // ========================
    // Administrations
    // ========================
    suspend fun getAdministrations(patientIpp: String? = null, status: String? = null): AdministrationListResponse =
        client.get("$baseUrl/administrations/") {
            parameter("patient_ipp", patientIpp)
            parameter("status", status)
            auth()
        }.body()

    suspend fun getTodayAdministrations(): List<AdministrationResponse> =
        client.get("$baseUrl/administrations/today") { auth() }.body()

    suspend fun recordAdministration(id: Int, request: RecordAdministrationRequest): AdministrationResponse =
        client.post("$baseUrl/administrations/$id/record") {
            setBody(request)
            auth()
        }.body()

    // ========================
    // Allergies
    // ========================
    suspend fun getAllergies(patientIpp: String? = null): AllergyListResponse =
        client.get("$baseUrl/allergies/") {
            parameter("patient_ipp", patientIpp)
            auth()
        }.body()

    suspend fun getPatientAllergies(patientIpp: String): List<PatientAllergyResponse> =
        client.get("$baseUrl/allergies/patient/$patientIpp") { auth() }.body()

    suspend fun createAllergy(patientIpp: String, allergenType: String, allergenName: String, atcCode: String?, severity: String, reactionType: String, confirmed: Boolean): PatientAllergyResponse =
        client.post("$baseUrl/allergies/") {
            contentType(ContentType.Application.Json)
            setBody(mapOf(
                "patient_ipp" to patientIpp,
                "allergen_type" to allergenType,
                "allergen_name" to allergenName,
                "atc_code" to (atcCode ?: ""),
                "severity" to severity,
                "reaction_type" to reactionType,
                "confirmed" to confirmed
            ))
            auth()
        }.body()

    // ========================
    // Dashboard
    // ========================
    suspend fun getDashboard(): DashboardResponse = client.get("$baseUrl/dashboard/") {
        auth()
    }.body()

    // ========================
    // Audit
    // ========================
    suspend fun getAuditLogs(action: String? = null, entityType: String? = null): AuditLogListResponse =
        client.get("$baseUrl/audit/") {
            parameter("action", action)
            parameter("entity_type", entityType)
            auth()
        }.body()

    // ========================
    // Entities
    // ========================

    suspend fun getEntities(skip: Int = 0, limit: Int = 100, includeInactive: Boolean = false): EntityListResponse =
        client.get("$baseUrl/entities/") {
            parameter("skip", skip)
            parameter("limit", limit)
            if (includeInactive) parameter("include_inactive", "true")
            auth()
        }.body()

    suspend fun getEntitiesBrief(): List<EntityBriefResponse> =
        client.get("$baseUrl/entities/brief") { auth() }.body()

    suspend fun getEntity(id: Int): EntityResponse =
        client.get("$baseUrl/entities/$id") { auth() }.body()

    suspend fun createEntity(request: Map<String, @UnsafeVariance Any>): EntityResponse =
        client.post("$baseUrl/entities/") {
            setBody(request)
            auth()
        }.body()

    suspend fun updateEntity(id: Int, request: Map<String, @UnsafeVariance Any>): EntityResponse =
        client.put("$baseUrl/entities/$id") {
            setBody(request)
            auth()
        }.body()

    suspend fun deleteEntity(id: Int): Unit =
        client.delete("$baseUrl/entities/$id") { auth() }.body()

    // User assignments
    suspend fun getMyEntities(): List<EntityBriefResponse> =
        client.get("$baseUrl/entities/me/entities") { auth() }.body()

    suspend fun getMyDefaultEntity(): EntityBriefResponse? =
        client.get("$baseUrl/entities/me/default-entity") { auth() }.body()

    suspend fun assignUserToEntity(request: CreateAssignmentRequest): EntityUserAssignmentResponse =
        client.post("$baseUrl/entities/assignments") {
            setBody(request)
            auth()
        }.body()

    suspend fun updateAssignment(id: Int, request: Map<String, @UnsafeVariance Any>): EntityUserAssignmentResponse =
        client.put("$baseUrl/entities/assignments/$id") {
            setBody(request)
            auth()
        }.body()

    suspend fun removeAssignment(id: Int): Unit =
        client.delete("$baseUrl/entities/assignments/$id") { auth() }.body()

    // Entity services
    suspend fun getEntityServices(entityId: Int, includeInactive: Boolean = false): EntityServiceListResponse =
        client.get("$baseUrl/entities/$entityId/services") {
            if (includeInactive) parameter("include_inactive", "true")
            auth()
        }.body()

    suspend fun createEntityService(entityId: Int, request: Map<String, @UnsafeVariance Any>): EntityServiceResponse =
        client.post("$baseUrl/entities/$entityId/services") {
            setBody(request)
            auth()
        }.body()

    // ========================
    // Settings
    // ========================

    suspend fun getSettings(
        group: String? = null,
        entityId: Int? = null,
        skip: Int = 0,
        limit: Int = 100
    ): SystemConfigListResponse = client.get("$baseUrl/settings/") {
        parameter("skip", skip)
        parameter("limit", limit)
        group?.let { parameter("group", it) }
        entityId?.let { parameter("entity_id", it) }
        auth()
    }.body()

    suspend fun getSettingsGrouped(entityId: Int? = null): List<SettingsGroupResponse> {
        val params = entityId?.let { "?entity_id=$it" } ?: ""
        return client.get("$baseUrl/settings/grouped$params") { auth() }.body()
    }

    suspend fun getSettingByKey(key: String, entityId: Int? = null): SystemConfigResponse {
        val params = entityId?.let { "?entity_id=$it" } ?: ""
        return client.get("$baseUrl/settings/by-key/$key$params") { auth() }.body()
    }

    suspend fun updateSettingByKey(key: String, value: String, entityId: Int? = null): SystemConfigResponse {
        val params = entityId?.let { "?entity_id=$it" } ?: ""
        return client.put("$baseUrl/settings/by-key/$key$params") {
            parameter("value", value)
            auth()
        }.body()
    }

    suspend fun bulkUpdateSettings(updates: List<ConfigUpdateRequest>, entityId: Int? = null): List<SystemConfigResponse> {
        val params = entityId?.let { "?entity_id=$it" } ?: ""
        return client.post("$baseUrl/settings/bulk-update$params") {
            setBody(BulkUpdateRequest(updates))
            auth()
        }.body()
    }

    suspend fun seedSettings(): Map<String, String> =
        client.post("$baseUrl/settings/seed") { auth() }.body()

    suspend fun getPublicSettingsGrouped(entityId: Int? = null): List<SettingsGroupResponse> {
        val params = entityId?.let { "?entity_id=$it" } ?: ""
        return client.get("$baseUrl/settings/public/grouped$params") { auth() }.body()
    }
}
