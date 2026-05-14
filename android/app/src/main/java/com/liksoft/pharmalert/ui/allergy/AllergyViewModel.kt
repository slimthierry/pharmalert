package com.liksoft.pharmalert.ui.allergy

import androidx.lifecycle.*
import com.liksoft.pharmalert.data.dto.PatientAllergyResponse
import com.liksoft.pharmalert.util.SessionManager
import kotlinx.coroutines.launch

class AllergyViewModel : ViewModel() {

    private val api = SessionManager.api

    private val _uiState = MutableLiveData<AllergyUiState>(AllergyUiState.Loading)
    val uiState: LiveData<AllergyUiState> = _uiState

    private val _allergies = MutableLiveData<List<PatientAllergyResponse>>()
    val allergies: LiveData<List<PatientAllergyResponse>> = _allergies

    private val _summary = MutableLiveData<AllergySummary>()
    val summary: LiveData<AllergySummary> = _summary

    private var currentPatientIpp: String? = null

    init { loadAllergies() }

    fun loadAllergies(patientIpp: String? = null) {
        currentPatientIpp = patientIpp
        _uiState.value = AllergyUiState.Loading
        viewModelScope.launch {
            try {
                val response = api.getAllergies(patientIpp = patientIpp)
                _allergies.value = response.allergies
                updateSummary(response.allergies)
                _uiState.value = if (response.allergies.isEmpty())
                    AllergyUiState.Empty
                else
                    AllergyUiState.Success(response.allergies)
            } catch (e: Exception) {
                _uiState.value = AllergyUiState.Error(e.localizedMessage ?: "Erreur inconnue")
            }
        }
    }

    private fun updateSummary(list: List<PatientAllergyResponse>) {
        _summary.value = AllergySummary(
            lifeThreatening = list.count { it.severity == "life_threatening" },
            severe = list.count { it.severity == "severe" },
            confirmed = list.count { it.confirmed }
        )
    }

    fun refresh() { loadAllergies(currentPatientIpp) }
}

data class AllergySummary(
    val lifeThreatening: Int,
    val severe: Int,
    val confirmed: Int
)

sealed class AllergyUiState {
    data object Loading : AllergyUiState()
    data object Empty : AllergyUiState()
    data class Success(val allergies: List<PatientAllergyResponse>) : AllergyUiState()
    data class Error(val message: String) : AllergyUiState()
}
