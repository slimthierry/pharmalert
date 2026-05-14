package com.liksoft.pharmalert.ui.audit

import androidx.lifecycle.*
import com.liksoft.pharmalert.data.dto.AuditLogResponse
import com.liksoft.pharmalert.util.SessionManager
import kotlinx.coroutines.launch

class AuditViewModel : ViewModel() {

    private val api = SessionManager.api

    private val _uiState = MutableLiveData<AuditUiState>(AuditUiState.Loading)
    val uiState: LiveData<AuditUiState> = _uiState

    private val _logs = MutableLiveData<List<AuditLogResponse>>()
    val logs: LiveData<List<AuditLogResponse>> = _logs

    private var currentAction: String? = null
    private var currentEntityType: String? = null

    init { loadLogs() }

    fun loadLogs(action: String? = null, entityType: String? = null) {
        currentAction = action
        currentEntityType = entityType
        _uiState.value = AuditUiState.Loading
        viewModelScope.launch {
            try {
                val response = api.getAuditLogs(action, entityType)
                _logs.value = response.logs
                _uiState.value = if (response.logs.isEmpty())
                    AuditUiState.Empty
                else
                    AuditUiState.Success(response.logs)
            } catch (e: Exception) {
                _uiState.value = AuditUiState.Error(e.localizedMessage ?: "Erreur inconnue")
            }
        }
    }

    fun refresh() { loadLogs(currentAction, currentEntityType) }
}

sealed class AuditUiState {
    data object Loading : AuditUiState()
    data object Empty : AuditUiState()
    data class Success(val logs: List<AuditLogResponse>) : AuditUiState()
    data class Error(val message: String) : AuditUiState()
}