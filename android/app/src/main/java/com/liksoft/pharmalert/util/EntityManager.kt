package com.liksoft.pharmalert.util

import android.content.Context
import android.content.SharedPreferences
import com.liksoft.pharmalert.data.dto.EntityBriefResponse

object EntityManager {

    private lateinit var prefs: SharedPreferences

    private var _currentEntity: EntityBriefResponse? = null
    private var _entities: List<EntityBriefResponse> = emptyList()

    val currentEntity: EntityBriefResponse? get() = _currentEntity
    val currentEntityId: Int? get() = _currentEntity?.id
    val entities: List<EntityBriefResponse> get() = _entities

    private var _isLoading: Boolean = false
    val isLoading: Boolean get() = _isLoading

    fun init(context: Context) {
        prefs = context.getSharedPreferences("pharmalert_entities", Context.MODE_PRIVATE)
    }

    fun setEntities(entities: List<EntityBriefResponse>) {
        _entities = entities
    }

    fun setCurrentEntity(entity: EntityBriefResponse?) {
        _currentEntity = entity
        entity?.let {
            prefs.edit().putInt(KEY_ENTITY_ID, it.id).apply()
        } ?: prefs.edit().remove(KEY_ENTITY_ID).apply()
    }

    fun selectEntity(entity: EntityBriefResponse) {
        setCurrentEntity(entity)
        prefs.edit().putInt(KEY_ENTITY_ID, entity.id).apply()
    }

    fun getSavedEntityId(): Int? {
        val id = prefs.getInt(KEY_ENTITY_ID, -1)
        return if (id == -1) null else id
    }

    fun restoreSavedEntity(): EntityBriefResponse? {
        val savedId = getSavedEntityId() ?: return null
        return _entities.find { it.id == savedId }
    }

    suspend fun loadAndRestoreEntity(): EntityBriefResponse? {
        val saved = restoreSavedEntity()
        if (saved != null) {
            _currentEntity = saved
            return saved
        }
        // No saved entity, try to get default from API
        return null
    }

    suspend fun loadEntitiesFromApi(): EntityBriefResponse? {
        _isLoading = true
        return try {
            val myEntities = SessionManager.api.getMyEntities()
            _entities = myEntities
            android.util.Log.d("EntityManager", "Loaded ${myEntities.size} entities")

            // Restore saved entity or use default
            val saved = restoreSavedEntity()
            if (saved != null) {
                _currentEntity = saved
                saved
            } else {
                try {
                    val default = SessionManager.api.getMyDefaultEntity()
                    _currentEntity = default
                    default?.let { selectEntity(it) }
                    default
                } catch (e: Exception) {
                    // No default entity yet — use first entity if available
                    android.util.Log.w("EntityManager", "No default entity, using first: ${e.message}")
                    if (myEntities.isNotEmpty()) {
                        val first = myEntities.first()
                        _currentEntity = first
                        selectEntity(first)
                        first
                    } else null
                }
            }
        } catch (e: Exception) {
            android.util.Log.e("EntityManager", "Failed to load entities", e)
            null
        } finally {
            _isLoading = false
        }
    }

    fun clear() {
        _currentEntity = null
        _entities = emptyList()
        prefs.edit().clear().apply()
    }

    private const val KEY_ENTITY_ID = "current_entity_id"
}
