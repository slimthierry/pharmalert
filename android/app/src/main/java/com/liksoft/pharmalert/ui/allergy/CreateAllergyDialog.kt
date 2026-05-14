package com.liksoft.pharmalert.ui.allergy

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.fragment.app.DialogFragment
import androidx.lifecycle.lifecycleScope
import com.liksoft.pharmalert.R
import com.liksoft.pharmalert.databinding.DialogCreateAllergyBinding
import com.liksoft.pharmalert.util.SessionManager
import kotlinx.coroutines.launch

class CreateAllergyDialog : DialogFragment() {

    private var _binding: DialogCreateAllergyBinding? = null
    private val binding get() = _binding!!

    private var onSuccess: (() -> Unit)? = null

    companion object {
        fun newInstance(onSuccess: () -> Unit = {}): CreateAllergyDialog {
            return CreateAllergyDialog().apply {
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
        _binding = DialogCreateAllergyBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupDropdowns()
        setupButtons()
    }

    private fun setupDropdowns() {
        // Types d'allergenes
        val types = listOf("medication", "food", "environmental", "other")
        binding.actvAllergenType.setAdapter(
            ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, types)
        )

        // Niveaux de severite
        val severities = listOf("mild", "moderate", "severe", "life_threatening")
        binding.actvSeverity.setAdapter(
            ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, severities)
        )
    }

    private fun setupButtons() {
        binding.btnCancel.setOnClickListener { dismiss() }
        binding.btnSubmit.setOnClickListener { submit() }
    }

    fun submit() {
        val ipp = binding.etPatientIpp.text.toString().trim()
        val allergenType = binding.actvAllergenType.text.toString().trim()
        val allergenName = binding.etAllergenName.text.toString().trim()
        val atcCode = binding.etAtcCode.text.toString().trim().takeIf { it.isNotBlank() }
        val severity = binding.actvSeverity.text.toString().trim()
        val reactionType = binding.etReactionType.text.toString().trim()
        val confirmed = binding.cbConfirmed.isChecked

        // Validation
        if (ipp.isEmpty()) { binding.tilPatientIpp.error = "IPP requis"; return }
        if (allergenType.isEmpty()) { binding.tilAllergenType.error = "Type requis"; return }
        if (allergenName.isEmpty()) { binding.tilAllergenName.error = "Nom requis"; return }
        if (severity.isEmpty()) { binding.tilSeverity.error = "Severite requise"; return }
        if (reactionType.isEmpty()) { binding.tilReactionType.error = "Reaction requise"; return }

        binding.tilPatientIpp.error = null
        binding.tilAllergenType.error = null
        binding.tilAllergenName.error = null
        binding.tilSeverity.error = null
        binding.tilReactionType.error = null

        setLoading(true)

        lifecycleScope.launch {
            try {
                SessionManager.api.createAllergy(
                    patientIpp = ipp,
                    allergenType = allergenType,
                    allergenName = allergenName,
                    atcCode = atcCode,
                    severity = severity,
                    reactionType = reactionType,
                    confirmed = confirmed
                )

                Toast.makeText(requireContext(), "Allergie ajoutee avec succes", Toast.LENGTH_SHORT).show()
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
        binding.actvAllergenType.isEnabled = !loading
        binding.etAllergenName.isEnabled = !loading
        binding.etAtcCode.isEnabled = !loading
        binding.actvSeverity.isEnabled = !loading
        binding.etReactionType.isEnabled = !loading
        binding.cbConfirmed.isEnabled = !loading
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}