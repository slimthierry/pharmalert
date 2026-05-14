package com.liksoft.pharmalert.ui.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.liksoft.pharmalert.R
import com.liksoft.pharmalert.data.dto.PatientAllergyResponse
import com.liksoft.pharmalert.databinding.ItemAllergyBinding

class AllergyAdapter : ListAdapter<PatientAllergyResponse, AllergyAdapter.ViewHolder>(DiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemAllergyBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ViewHolder(private val binding: ItemAllergyBinding) : RecyclerView.ViewHolder(binding.root) {

        fun bind(item: PatientAllergyResponse) {
            binding.tvAllergen.text = item.allergenName
            binding.tvPatientIpp.text = "IPP: ${item.patientIpp}"
            binding.tvType.text = item.allergenType.replaceFirstChar { it.uppercase() }
            if (!item.atcCode.isNullOrBlank()) {
                binding.tvAtcCode.text = "ATC: ${item.atcCode}"
            }

            val (severityText, severityColor) = when (item.severity) {
                "life_threatening" -> "Vitale" to R.color.severity_contraindicated
                "severe" -> "Severe" to R.color.severity_major
                "moderate" -> "Moderee" to R.color.severity_moderate
                else -> "Legere" to R.color.severity_minor
            }

            binding.chipSeverity.text = severityText
            binding.chipSeverity.setChipBackgroundColorResource(severityColor)
            binding.tvReaction.text = "Reaction: ${item.reactionType.replaceFirstChar { it.uppercase() }}"

            if (item.confirmed) {
                binding.ivConfirmed.setImageResource(android.R.drawable.checkbox_on_background)
            }
        }
    }

    class DiffCallback : DiffUtil.ItemCallback<PatientAllergyResponse>() {
        override fun areItemsTheSame(old: PatientAllergyResponse, new: PatientAllergyResponse) = old.id == new.id
        override fun areContentsTheSame(old: PatientAllergyResponse, new: PatientAllergyResponse) = old == new
    }
}
