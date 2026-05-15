package com.liksoft.pharmalert.ui.interaction

import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.core.content.ContextCompat
import androidx.fragment.app.DialogFragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.liksoft.pharmalert.R
import com.liksoft.pharmalert.data.dto.InteractionCheckResult
import com.liksoft.pharmalert.data.dto.InteractionCheckResponse
import com.liksoft.pharmalert.data.dto.MedicationResponse
import com.liksoft.pharmalert.databinding.DialogCheckInteractionsBinding
import com.liksoft.pharmalert.util.SessionManager
import com.google.android.material.chip.Chip
import kotlinx.coroutines.launch

class CheckInteractionDialog : DialogFragment() {

    private var _binding: DialogCheckInteractionsBinding? = null
    private val binding get() = _binding!!

    private val selectedMedicationIds = mutableListOf<Int>()
    private val allMedications = mutableListOf<MedicationResponse>()
    private val filteredMedications = mutableListOf<MedicationResponse>()
    private lateinit var adapter: MedicationSelectionAdapter

    private var onSuccess: (() -> Unit)? = null

    companion object {
        fun newInstance(onSuccess: () -> Unit = {}): CheckInteractionDialog {
            return CheckInteractionDialog().apply {
                this.onSuccess = onSuccess
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setStyle(STYLE_NORMAL, R.style.Theme_PharmAlert)
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = DialogCheckInteractionsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupRecyclerView()
        setupSearch()
        setupButtons()
        loadMedications()
    }

    private fun setupRecyclerView() {
        adapter = MedicationSelectionAdapter(
            onMedicationSelected = { medication, selected ->
                if (selected) {
                    selectedMedicationIds.add(medication.id)
                } else {
                    selectedMedicationIds.remove(medication.id)
                }
                updateSelectedCount()
                updateSelectedChips()
                binding.btnCheck.isEnabled = selectedMedicationIds.size >= 2
            },
            selectedIds = selectedMedicationIds
        )
        binding.rvMedications.layoutManager = LinearLayoutManager(requireContext())
        binding.rvMedications.adapter = adapter
    }

    private fun setupSearch() {
        binding.etSearch.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                val query = s?.toString()?.lowercase() ?: ""
                filteredMedications.clear()
                filteredMedications.addAll(
                    if (query.isEmpty()) allMedications
                    else allMedications.filter { it.name.lowercase().contains(query) }
                )
                adapter.submitList(filteredMedications.toList())
            }
        })
    }

    private fun setupButtons() {
        binding.btnCancel.setOnClickListener { dismiss() }
        binding.btnCheck.setOnClickListener { checkInteractions() }
    }

    private fun loadMedications() {
        lifecycleScope.launch {
            try {
                val response = SessionManager.api.getMedications(limit = 100)
                allMedications.clear()
                allMedications.addAll(response.medications)
                filteredMedications.clear()
                filteredMedications.addAll(response.medications)
                adapter.submitList(filteredMedications.toList())
            } catch (e: Exception) {
                Toast.makeText(requireContext(), "Erreur chargement medicaments", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun updateSelectedCount() {
        binding.tvSelectedCount.text = "${selectedMedicationIds.size} medicament(s) selectionne(s)"
    }

    private fun updateSelectedChips() {
        binding.chipGroupSelected.removeAllViews()
        allMedications.filter { it.id in selectedMedicationIds }.forEach { med ->
            val chip = Chip(requireContext()).apply {
                text = med.name
                isCloseIconVisible = true
                setOnCloseIconClickListener {
                    selectedMedicationIds.remove(med.id)
                    adapter.notifyDataSetChanged()
                    updateSelectedCount()
                    updateSelectedChips()
                    binding.btnCheck.isEnabled = selectedMedicationIds.size >= 2
                }
            }
            binding.chipGroupSelected.addView(chip)
        }
    }

    private fun checkInteractions() {
        binding.tvError.visibility = View.GONE
        binding.cardResults.visibility = View.GONE
        setLoading(true)

        val patientIpp = binding.etPatientIpp.text.toString().trim().takeIf { it.isNotBlank() }

        lifecycleScope.launch {
            try {
                val response = SessionManager.api.checkInteractions(selectedMedicationIds, patientIpp)
                setLoading(false)
                displayResults(response)
            } catch (e: Exception) {
                setLoading(false)
                binding.tvError.text = e.localizedMessage ?: "Erreur lors de la verification"
                binding.tvError.visibility = View.VISIBLE
            }
        }
    }

    private fun displayResults(response: InteractionCheckResponse) {
        binding.cardResults.visibility = View.VISIBLE

        // Title with color based on severity
        val color = when {
            response.has_contraindicated -> R.color.severity_contraindicated
            response.hasMajor -> R.color.severity_major
            response.hasModerate -> R.color.severity_moderate
            response.hasMinor -> R.color.severity_minor
            else -> R.color.brand_700
        }

        val titleText = if (response.interactions.isEmpty()) {
            "Aucune interaction trouvee"
        } else {
            "${response.interactions.size} interaction(s) trouvee(s)"
        }
        binding.tvResultTitle.text = titleText
        binding.tvResultTitle.setTextColor(ContextCompat.getColor(requireContext(), color))

        // Show results in RecyclerView
        val resultsAdapter = InteractionResultAdapter()
        binding.rvResults.layoutManager = LinearLayoutManager(requireContext())
        binding.rvResults.adapter = resultsAdapter
        resultsAdapter.submitList(response.interactions)

        // Also show summary
        val summaryLines = mutableListOf<String>()
        if (response.has_contraindicated) summaryLines.add("⚠ Contre-indique")
        if (response.hasMajor) summaryLines.add("🔴 Majeur")
        if (response.hasModerate) summaryLines.add("🟡 Moderé")
        if (response.hasMinor) summaryLines.add("🟢 Mineur")

        if (summaryLines.isNotEmpty()) {
            Toast.makeText(requireContext(), summaryLines.joinToString(" | "), Toast.LENGTH_LONG).show()
        }
    }

    private fun setLoading(loading: Boolean) {
        binding.progressBar.visibility = if (loading) View.VISIBLE else View.GONE
        binding.btnCheck.isEnabled = !loading && selectedMedicationIds.size >= 2
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}