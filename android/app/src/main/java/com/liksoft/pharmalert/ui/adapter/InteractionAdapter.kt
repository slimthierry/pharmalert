package com.liksoft.pharmalert.ui.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.liksoft.pharmalert.R
import com.liksoft.pharmalert.data.dto.InteractionResponse
import com.liksoft.pharmalert.databinding.ItemInteractionBinding

class InteractionAdapter : ListAdapter<InteractionResponse, InteractionAdapter.ViewHolder>(DiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemInteractionBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ViewHolder(private val binding: ItemInteractionBinding) : RecyclerView.ViewHolder(binding.root) {

        private val severityColors = mapOf(
            "contraindicated" to Pair(R.color.severity_contraindicated, "Contre-indiquee"),
            "major" to Pair(R.color.severity_major, "Majeure"),
            "moderate" to Pair(R.color.severity_moderate, "Moderee"),
            "minor" to Pair(R.color.severity_minor, "Mineure")
        )

        fun bind(item: InteractionResponse) {
            val colorRes = severityColors[item.severity] ?: severityColors["minor"]!!

            binding.tvMedications.text = "${item.medicationAName} + ${item.medicationBName}"
            binding.tvSeverity.text = colorRes.second
            binding.tvClinicalEffect.text = item.clinicalEffect
            binding.tvRecommendation.text = item.recommendation ?: ""

            binding.cardSeverity.setCardBackgroundColor(
                binding.root.context.getColor(colorRes.first)
            )
        }
    }

    class DiffCallback : DiffUtil.ItemCallback<InteractionResponse>() {
        override fun areItemsTheSame(old: InteractionResponse, new: InteractionResponse) = old.id == new.id
        override fun areContentsTheSame(old: InteractionResponse, new: InteractionResponse) = old == new
    }
}
