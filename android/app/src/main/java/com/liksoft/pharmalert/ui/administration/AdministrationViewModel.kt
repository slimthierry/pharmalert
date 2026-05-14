package com.liksoft.pharmalert.ui.administration

import androidx.lifecycle.*
import com.liksoft.pharmalert.data.dto.AdministrationResponse
import com.liksoft.pharmalert.data.dto.RecordAdministrationRequest
import com.liksoft.pharmalert.util.SessionManager
import kotlinx.coroutines.launch

class AdministrationViewModel : ViewModel() {

    private val api = SessionManager.api

    private val _uiState = MutableLiveData<AdministrationUiState>(AdministrationUiState.Loading)
    val uiState: LiveData<AdministrationUiState> = _uiState

    private val _administrations = MutableLiveData<List<AdministrationResponse>>()
    val administrations: LiveData<List<AdministrationResponse>> = _administrations

    private val _recordResult = MutableLiveData<RecordResult?>()
    val recordResult: LiveData<RecordResult?> = _recordResult

    private var currentFilter: String? = null

    init { loadAdministrations() }

    fun loadAdministrations(status: String? = null) {
        currentFilter = status
        _uiState.value = AdministrationUiState.Loading
        viewModelScope.launch {
            try {
                val response = api.getAdministrations(status = status)
                _administrations.value = response.administrations
                _uiState.value = if (response.administrations.isEmpty())
                    AdministrationUiState.Empty
                else
                    AdministrationUiState.Success(response.administrations)
            } catch (e: Exception) {
                _uiState.value = AdministrationUiState.Error(e.localizedMessage ?: "Erreur inconnue")
            }
        }
    }

    fun recordAdministration(id: Int, status: String, doseGiven: Double?, notes: String?) {
        viewModelScope.launch {
            try {
                val result = api.recordAdministration(
                    id,
                    RecordAdministrationRequest(status, doseGiven, notes)
                )
                _recordResult.value = RecordResult.Success(result)
                refresh()
            } catch (e: Exception) {
                _recordResult.value = RecordResult.Error(e.localizedMessage ?: "Erreur")
            }
        }
    }

    fun clearRecordResult() { _recordResult.value = null }

    fun refresh() { loadAdministrations(currentFilter) }
}

sealed class AdministrationUiState {
    data object Loading : AdministrationUiState()
    data object Empty : AdministrationUiState()
    data class Success(val administrations: List<AdministrationResponse>) : AdministrationUiState()
    data class Error(val message: String) : AdministrationUiState()
}

sealed class RecordResult {
    data class Success(val administration: AdministrationResponse) : RecordResult()
    data class Error(val message: String) : RecordResult()
}
