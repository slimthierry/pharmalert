package com.liksoft.pharmalert.ui.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.liksoft.pharmalert.data.dto.PrescriptionResponse
import com.liksoft.pharmalert.databinding.ItemPrescriptionBinding

class PrescriptionAdapter : ListAdapter<PrescriptionResponse, PrescriptionAdapter.ViewHolder>(DiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemPrescriptionBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ViewHolder(private val binding: ItemPrescriptionBinding) : RecyclerView.ViewHolder(binding.root) {
        fun bind(item: PrescriptionResponse) {
            binding.tvPatientName.text = item.patientName
            binding.tvPatientIpp.text = "IPP: ${item.patientIpp}"
            binding.tvMedication.text = item.medicationName ?: "Medicament #${item.medicationId}"
            binding.tvDosage.text = "${item.dosageValue} ${item.dosageUnit} — ${item.frequency}"
            binding.tvRoute.text = "Voie: ${item.route}"
            binding.tvDoctor.text = "Dr. ${item.doctorName ?: "—" }"

            val statusColor = when (item.validationStatus) {
                "validated" -> "#22C55E"
                "rejected" -> "#EF4444"
                else -> "#F59E0B"
            }
            binding.chipStatus.text = when (item.validationStatus) {
                "validated" -> "Validee"
                "rejected" -> "Rejetee"
                else -> "En attente"
            }
            binding.chipStatus.setChipBackgroundColorResource(
                when (item.validationStatus) {
                    "validated" -> android.R.color.holo_green_light
                    "rejected" -> android.R.color.holo_red_light
                    else -> android.R.color.holo_orange_light
                }
            )
        }
    }

    class DiffCallback : DiffUtil.ItemCallback<PrescriptionResponse>() {
        override fun areItemsTheSame(old: PrescriptionResponse, new: PrescriptionResponse) = old.id == new.id
        override fun areContentsTheSame(old: PrescriptionResponse, new: PrescriptionResponse) = old == new
    }
}
