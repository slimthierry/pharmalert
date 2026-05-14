package com.liksoft.pharmalert.ui.prescription

import androidx.lifecycle.*
import com.liksoft.pharmalert.data.dto.PrescriptionResponse
import com.liksoft.pharmalert.util.SessionManager
import kotlinx.coroutines.launch

class PrescriptionViewModel : ViewModel() {

    private val api = SessionManager.api

    private val _uiState = MutableLiveData<PrescriptionUiState>(PrescriptionUiState.Loading)
    val uiState: LiveData<PrescriptionUiState> = _uiState

    private val _prescriptions = MutableLiveData<List<PrescriptionResponse>>()
    val prescriptions: LiveData<List<PrescriptionResponse>> = _prescriptions

    private var currentFilter: String? = null
    private var currentSearch: String? = null

    init { loadPrescriptions() }

    fun loadPrescriptions(status: String? = null, search: String? = null) {
        currentFilter = status
        currentSearch = search
        _uiState.value = PrescriptionUiState.Loading
        viewModelScope.launch {
            try {
                val response = api.getPrescriptions(patientIpp = search, status = status)
                _prescriptions.value = response.prescriptions
                _uiState.value = if (response.prescriptions.isEmpty())
                    PrescriptionUiState.Empty
                else
                    PrescriptionUiState.Success(response.prescriptions)
            } catch (e: Exception) {
                _uiState.value = PrescriptionUiState.Error(e.localizedMessage ?: "Erreur inconnue")
            }
        }
    }

    fun refresh() {
        loadPrescriptions(currentFilter, currentSearch)
    }
}

sealed class PrescriptionUiState {
    data object Loading : PrescriptionUiState()
    data object Empty : PrescriptionUiState()
    data class Success(val prescriptions: List<PrescriptionResponse>) : PrescriptionUiState()
    data class Error(val message: String) : PrescriptionUiState()
}
