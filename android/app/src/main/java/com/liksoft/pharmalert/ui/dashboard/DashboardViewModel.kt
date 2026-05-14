package com.liksoft.pharmalert.ui.dashboard

import androidx.lifecycle.*
import com.liksoft.pharmalert.data.dto.DashboardResponse
import com.liksoft.pharmalert.util.SessionManager
import kotlinx.coroutines.launch

class DashboardViewModel : ViewModel() {

    private val api = SessionManager.api

    private val _uiState = MutableLiveData<DashboardUiState>(DashboardUiState.Loading)
    val uiState: LiveData<DashboardUiState> = _uiState

    private val _dashboard = MutableLiveData<DashboardResponse>()
    val dashboard: LiveData<DashboardResponse> = _dashboard

    init {
        loadDashboard()
    }

    fun loadDashboard() {
        _uiState.value = DashboardUiState.Loading
        viewModelScope.launch {
            try {
                val data = api.getDashboard()
                _dashboard.value = data
                _uiState.value = DashboardUiState.Success(data)
            } catch (e: Exception) {
                _uiState.value = DashboardUiState.Error(e.localizedMessage ?: "Erreur inconnue")
            }
        }
    }

    fun refresh() {
        loadDashboard()
    }
}

sealed class DashboardUiState {
    data object Loading : DashboardUiState()
    data class Success(val data: DashboardResponse) : DashboardUiState()
    data class Error(val message: String) : DashboardUiState()
}