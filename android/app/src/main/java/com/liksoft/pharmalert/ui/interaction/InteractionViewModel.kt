package com.liksoft.pharmalert.ui.interaction

import androidx.lifecycle.*
import com.liksoft.pharmalert.data.dto.InteractionResponse
import com.liksoft.pharmalert.util.SessionManager
import kotlinx.coroutines.launch

class InteractionViewModel : ViewModel() {

    private val api = SessionManager.api

    private val _uiState = MutableLiveData<InteractionUiState>(InteractionUiState.Loading)
    val uiState: LiveData<InteractionUiState> = _uiState

    private val _interactions = MutableLiveData<List<InteractionResponse>>()
    val interactions: LiveData<List<InteractionResponse>> = _interactions

    private val _summary = MutableLiveData<InteractionSummary>()
    val summary: LiveData<InteractionSummary> = _summary

    init { loadInteractions() }

    fun loadInteractions(severity: String? = null) {
        _uiState.value = InteractionUiState.Loading
        viewModelScope.launch {
            try {
                val response = api.getInteractions(severity)
                _interactions.value = response.interactions
                updateSummary(response.interactions)
                _uiState.value = if (response.interactions.isEmpty())
                    InteractionUiState.Empty
                else
                    InteractionUiState.Success(response.interactions)
            } catch (e: Exception) {
                _uiState.value = InteractionUiState.Error(e.localizedMessage ?: "Erreur inconnue")
            }
        }
    }

    private fun updateSummary(list: List<InteractionResponse>) {
        _summary.value = InteractionSummary(
            contraindicated = list.count { it.severity == "contraindicated" },
            major = list.count { it.severity == "major" },
            moderate = list.count { it.severity == "moderate" },
            minor = list.count { it.severity == "minor" }
        )
    }

    fun refresh() { loadInteractions() }
}

data class InteractionSummary(
    val contraindicated: Int,
    val major: Int,
    val moderate: Int,
    val minor: Int
)

sealed class InteractionUiState {
    data object Loading : InteractionUiState()
    data object Empty : InteractionUiState()
    data class Success(val interactions: List<InteractionResponse>) : InteractionUiState()
    data class Error(val message: String) : InteractionUiState()
}
