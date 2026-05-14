package com.liksoft.pharmalert.ui.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.liksoft.pharmalert.R
import com.liksoft.pharmalert.data.dto.AdministrationResponse
import com.liksoft.pharmalert.databinding.ItemAdministrationBinding

class AdministrationAdapter(
    private val onItemClick: (AdministrationResponse) -> Unit
) : ListAdapter<AdministrationResponse, AdministrationAdapter.ViewHolder>(DiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemAdministrationBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return ViewHolder(binding, onItemClick)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ViewHolder(
        private val binding: ItemAdministrationBinding,
        private val onItemClick: (AdministrationResponse) -> Unit
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(item: AdministrationResponse) {
            binding.tvPatient.text = item.patientName ?: "Patient #${item.patientIpp}"
            binding.tvPatientIpp.text = "IPP: ${item.patientIpp}"
            binding.tvMedication.text = item.medicationName ?: "Medicament"
            binding.tvScheduledAt.text = item.scheduledAt.take(16).replace("T", " ")

            val (statusText, statusColor) = when (item.status) {
                "given" -> "Donne" to R.color.status_given
                "refused" -> "Refuse" to R.color.status_refused
                "delayed" -> "Retarde" to R.color.status_pending
                "missed" -> "Oubli" to R.color.status_pending
                else -> "En attente" to R.color.status_pending
            }

            binding.chipStatus.text = statusText
            binding.chipStatus.setChipBackgroundColorResource(statusColor)

            binding.root.setOnClickListener { onItemClick(item) }
        }
    }

    class DiffCallback : DiffUtil.ItemCallback<AdministrationResponse>() {
        override fun areItemsTheSame(old: AdministrationResponse, new: AdministrationResponse) = old.id == new.id
        override fun areContentsTheSame(old: AdministrationResponse, new: AdministrationResponse) = old == new
    }
}
