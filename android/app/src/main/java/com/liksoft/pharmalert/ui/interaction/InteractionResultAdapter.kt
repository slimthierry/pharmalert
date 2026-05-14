package com.liksoft.pharmalert.ui.interaction

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.liksoft.pharmalert.R
import com.liksoft.pharmalert.data.dto.InteractionCheckResult
import com.liksoft.pharmalert.databinding.ItemInteractionResultBinding

class InteractionResultAdapter : ListAdapter<InteractionCheckResult, InteractionResultAdapter.VH>(Diff()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val binding = ItemInteractionResultBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return VH(binding)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        holder.bind(getItem(position))
    }

    class VH(private val binding: ItemInteractionResultBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(item: InteractionCheckResult) {
            binding.tvMedications.text = "${item.medicationAName} + ${item.medicationBName}"
            binding.tvSeverity.text = item.severity.replaceFirstChar { it.uppercase() }
            binding.tvEffect.text = item.clinicalEffect
            binding.tvRecommendation.text = item.recommendation ?: ""

            val severityColor = when (item.severity) {
                "contraindicated" -> R.color.severity_contraindicated
                "major" -> R.color.severity_major
                "moderate" -> R.color.severity_moderate
                "minor" -> R.color.severity_minor
                else -> R.color.gray_500
            }
            binding.severityIndicator.setBackgroundColor(
                ContextCompat.getColor(binding.root.context, severityColor)
            )
            binding.tvSeverity.setTextColor(
                ContextCompat.getColor(binding.root.context, severityColor)
            )
        }
    }

    class Diff : DiffUtil.ItemCallback<InteractionCheckResult>() {
        override fun areItemsTheSame(old: InteractionCheckResult, new: InteractionCheckResult) =
            old.id == new.id
        override fun areContentsTheSame(old: InteractionCheckResult, new: InteractionCheckResult) =
            old == new
    }
}