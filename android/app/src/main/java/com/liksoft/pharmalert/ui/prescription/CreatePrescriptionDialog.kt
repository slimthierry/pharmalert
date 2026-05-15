package com.liksoft.pharmalert.ui.prescription

import android.app.DatePickerDialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.fragment.app.DialogFragment
import androidx.lifecycle.lifecycleScope
import com.liksoft.pharmalert.R
import com.liksoft.pharmalert.data.dto.CreatePrescriptionRequest
import com.liksoft.pharmalert.data.dto.MedicationResponse
import com.liksoft.pharmalert.databinding.DialogCreatePrescriptionBinding
import com.liksoft.pharmalert.util.SessionManager
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

class CreatePrescriptionDialog : DialogFragment() {

    private var _binding: DialogCreatePrescriptionBinding? = null
    private val binding get() = _binding!!

    private var selectedMedication: MedicationResponse? = null
    private var medications: List<MedicationResponse> = emptyList()
    private var startDate: String = ""
    private var onSuccess: (() -> Unit)? = null

    private val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())

    companion object {
        fun newInstance(onSuccess: () -> Unit = {}): CreatePrescriptionDialog {
            return CreatePrescriptionDialog().apply {
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
        _binding = DialogCreatePrescriptionBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupDropdowns()
        setupDatePicker()
        setupButtons()
        loadMedications()
    }

    private fun setupButtons() {
        binding.btnCancel.setOnClickListener { dismiss() }
        binding.btnSubmit.setOnClickListener { submit() }
    }

    private fun setupDropdowns() {
        // Unités
        val units = listOf("mg", "ml", "g", "mcg", "UI", "ml")
        binding.actvDosageUnit.setAdapter(
            ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, units)
        )

        // Fréquences
        val frequencies = listOf("1x/jour", "2x/jour", "3x/jour", "4x/jour", "1x/semaine", "2x/semaine", "Toutes les 8h", "Toutes les 12h")
        binding.actvFrequency.setAdapter(
            ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, frequencies)
        )

        // Voies
        val routes = listOf("orale", "IV", "IM", "SC", "rectale", "inhalation", "cutanee", "oculaire", "OTIQUE")
        binding.actvRoute.setAdapter(
            ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, routes)
        )
    }

    private fun setupDatePicker() {
        // Set today's date by default
        startDate = dateFormat.format(Date())
        binding.etStartDate.setText(startDate)

        binding.etStartDate.setOnClickListener {
            val calendar = Calendar.getInstance()
            DatePickerDialog(
                requireContext(),
                { _, year, month, day ->
                    calendar.set(year, month, day)
                    startDate = dateFormat.format(calendar.time)
                    binding.etStartDate.setText(startDate)
                },
                calendar.get(Calendar.YEAR),
                calendar.get(Calendar.MONTH),
                calendar.get(Calendar.DAY_OF_MONTH)
            ).show()
        }
    }

    private fun loadMedications() {
        binding.tilMedication.isEnabled = false
        lifecycleScope.launch {
            try {
                android.util.Log.d("CreatePrescriptionDialog", "Fetching medications from API...")
                val response = SessionManager.api.getMedications(limit = 100)
                android.util.Log.d("CreatePrescriptionDialog", "Response received: ${response.medications.size} medications")

                medications = response.medications

                if (medications.isEmpty()) {
                    Toast.makeText(requireContext(), "Aucun medicament trouve. Ajoutez des medicaments d'abord.", Toast.LENGTH_LONG).show()
                    return@launch
                }

                val names = medications.map { "${it.name} - ${it.dosage ?: ""}".trim() }
                android.util.Log.d("CreatePrescriptionDialog", "Adapter items: ${names.take(3)}")

                val adapter = ArrayAdapter(requireContext(), R.layout.item_dropdown, names)
                binding.actvMedication.setAdapter(adapter)
                binding.actvMedication.isEnabled = true
                binding.tilMedication.isEnabled = true

                binding.actvMedication.setOnItemClickListener { _, _, position, _ ->
                    android.util.Log.d("CreatePrescriptionDialog", "Item clicked at position $position: ${names.getOrNull(position)}")
                    selectedMedication = medications.getOrNull(position)
                    binding.tilMedication.error = null
                }

                android.util.Log.d("CreatePrescriptionDialog", "Medication dropdown ready. Count: ${medications.size}")
            } catch (e: Exception) {
                android.util.Log.e("CreatePrescriptionDialog", "Failed to load medications", e)
                Toast.makeText(requireContext(), "Erreur chargement medicaments: ${e.localizedMessage}", Toast.LENGTH_LONG).show()
            }
        }
    }

    fun submit() {
        val ipp = binding.etPatientIpp.text.toString().trim()
        val name = binding.etPatientName.text.toString().trim()
        val dosageStr = binding.etDosageValue.text.toString().trim()
        val unit = binding.actvDosageUnit.text.toString().trim()
        val frequency = binding.actvFrequency.text.toString().trim()
        val route = binding.actvRoute.text.toString().trim()

        // Validation
        if (ipp.isEmpty()) { binding.tilPatientIpp.error = "IPP requis"; return }
        if (name.isEmpty()) { binding.tilPatientName.error = "Nom requis"; return }
        if (selectedMedication == null) { binding.tilMedication.error = "Medicament requis"; return }
        if (dosageStr.isEmpty()) { binding.tilDosageValue.error = "Dosage requis"; return }
        if (unit.isEmpty()) { binding.tilDosageUnit.error = "Unite requise"; return }
        if (frequency.isEmpty()) { binding.tilFrequency.error = "Frequence requise"; return }
        if (route.isEmpty()) { binding.tilRoute.error = "Voie requise"; return }

        binding.tilPatientIpp.error = null
        binding.tilPatientName.error = null
        binding.tilMedication.error = null
        binding.tilDosageValue.error = null
        binding.tilDosageUnit.error = null
        binding.tilFrequency.error = null
        binding.tilRoute.error = null

        setLoading(true)

        lifecycleScope.launch {
            try {
                val request = CreatePrescriptionRequest(
                    patientIpp = ipp,
                    patientName = name,
                    medicationId = selectedMedication!!.id,
                    dosageValue = dosageStr.toDoubleOrNull() ?: 0.0,
                    dosageUnit = unit,
                    frequency = frequency,
                    route = route,
                    startDate = startDate
                )

                val response = SessionManager.api.createPrescription(request)

                // Afficher les warnings d'allergie et interactions
                val warnings = mutableListOf<String>()
                if (response.allergyWarnings.isNotEmpty()) {
                    warnings.addAll(response.allergyWarnings)
                }
                if (response.interactions.isNotEmpty()) {
                    warnings.add("${response.interactions.size} interaction(s) medicamenteuse(s) detectee(s)")
                }

                if (warnings.isNotEmpty()) {
                    Toast.makeText(requireContext(), warnings.joinToString("\n"), Toast.LENGTH_LONG).show()
                } else {
                    Toast.makeText(requireContext(), "Prescription creee avec succes", Toast.LENGTH_SHORT).show()
                }

                onSuccess?.invoke()
                dismiss()
            } catch (e: Exception) {
                setLoading(false)
                binding.tvError.text = e.localizedMessage ?: "Erreur lors de la creation"
                binding.tvError.visibility = View.VISIBLE
            }
        }
    }

    private fun setLoading(loading: Boolean) {
        binding.progressBar.visibility = if (loading) View.VISIBLE else View.GONE
        binding.etPatientIpp.isEnabled = !loading
        binding.etPatientName.isEnabled = !loading
        binding.actvMedication.isEnabled = !loading
        binding.etDosageValue.isEnabled = !loading
        binding.actvDosageUnit.isEnabled = !loading
        binding.actvFrequency.isEnabled = !loading
        binding.actvRoute.isEnabled = !loading
        binding.etStartDate.isEnabled = !loading
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
