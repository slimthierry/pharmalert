package com.liksoft.pharmalert.data.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// ========================
// Entity DTOs
// ========================

@Serializable
data class EntityBriefResponse(
    val id: Int,
    val name: String,
    val code: String,
    @SerialName("logo_url") val logoUrl: String? = null,
    @SerialName("is_active") val isActive: Boolean
)

@Serializable
data class EntityResponse(
    val id: Int,
    val name: String,
    val code: String,
    val description: String? = null,
    val address: String? = null,
    val phone: String? = null,
    val email: String? = null,
    val city: String? = null,
    val country: String? = null,
    @SerialName("logo_url") val logoUrl: String? = null,
    @SerialName("is_active") val isActive: Boolean,
    @SerialName("is_default") val isDefault: Boolean,
    @SerialName("subscription_start") val subscriptionStart: String? = null,
    @SerialName("subscription_end") val subscriptionEnd: String? = null,
    @SerialName("max_users") val maxUsers: Int = 50,
    @SerialName("is_subscription_valid") val isSubscriptionValid: Boolean = true,
    @SerialName("created_at") val createdAt: String,
    @SerialName("updated_at") val updatedAt: String
)

@Serializable
data class EntityListResponse(
    val entities: List<EntityResponse>,
    val total: Int
)

@Serializable
data class EntityServiceResponse(
    val id: Int,
    @SerialName("entity_id") val entityId: Int,
    val name: String,
    val code: String,
    val description: String? = null,
    val category: String? = null,
    @SerialName("is_active") val isActive: Boolean,
    @SerialName("display_order") val displayOrder: Int,
    @SerialName("created_at") val createdAt: String
)

@Serializable
data class EntityServiceListResponse(
    val services: List<EntityServiceResponse>,
    val total: Int
)

@Serializable
data class EntityUserAssignmentResponse(
    val id: Int,
    @SerialName("user_id") val userId: Int,
    @SerialName("entity_id") val entityId: Int,
    @SerialName("is_default") val isDefault: Boolean,
    @SerialName("start_date") val startDate: String? = null,
    @SerialName("end_date") val endDate: String? = null,
    @SerialName("is_active") val isActive: Boolean,
    @SerialName("assigned_by") val assignedBy: Int? = null,
    @SerialName("assignment_reason") val assignmentReason: String? = null,
    @SerialName("is_valid") val isValid: Boolean,
    @SerialName("created_at") val createdAt: String
)

@Serializable
data class CreateAssignmentRequest(
    @SerialName("user_id") val userId: Int,
    @SerialName("entity_id") val entityId: Int,
    @SerialName("is_default") val isDefault: Boolean = false,
    @SerialName("assignment_reason") val assignmentReason: String? = null
)

// ========================
// Settings / Config DTOs
// ========================

@Serializable
data class ConfigGroupResponse(
    val id: Int,
    val key: String,
    val name: String,
    val description: String? = null,
    val icon: String? = null,
    @SerialName("display_order") val displayOrder: Int,
    @SerialName("is_active") val isActive: Boolean
)

@Serializable
data class SystemConfigResponse(
    val id: Int,
    val key: String,
    val value: String? = null,
    val group: String,
    val description: String? = null,
    @SerialName("display_name") val displayName: String? = null,
    @SerialName("is_secret") val isSecret: Boolean,
    @SerialName("is_required") val isRequired: Boolean,
    @SerialName("is_editable") val isEditable: Boolean = true,
    @SerialName("value_type") val valueType: String,
    @SerialName("default_value") val defaultValue: String? = null,
    val choices: String? = null,
    @SerialName("is_global") val isGlobal: Boolean,
    @SerialName("entity_id") val entityId: Int? = null,
    @SerialName("created_at") val createdAt: String,
    @SerialName("updated_at") val updatedAt: String
)

@Serializable
data class SystemConfigListResponse(
    val configs: List<SystemConfigResponse>,
    val total: Int
)

@Serializable
data class SettingsGroupResponse(
    val group: String,
    @SerialName("group_name") val groupName: String,
    val icon: String? = null,
    val configs: List<SystemConfigItemResponse>
)

@Serializable
data class SystemConfigItemResponse(
    val key: String,
    val value: String? = null,
    @SerialName("display_name") val displayName: String? = null
)

@Serializable
data class ConfigUpdateRequest(
    val key: String,
    val value: String
)

@Serializable
data class BulkUpdateRequest(
    val updates: List<ConfigUpdateRequest>
)