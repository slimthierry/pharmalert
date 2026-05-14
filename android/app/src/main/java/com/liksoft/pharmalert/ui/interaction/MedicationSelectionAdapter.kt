package com.liksoft.pharmalert.ui.interaction

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.liksoft.pharmalert.data.dto.MedicationResponse
import com.liksoft.pharmalert.databinding.ItemMedicationSelectionBinding

class MedicationSelectionAdapter(
    private val onMedicationSelected: (MedicationResponse, Boolean) -> Unit,
    private val selectedIds: MutableList<Int>
) : ListAdapter<MedicationResponse, MedicationSelectionAdapter.VH>(Diff()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val binding = ItemMedicationSelectionBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return VH(binding)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        holder.bind(getItem(position))
    }

    inner class VH(private val binding: ItemMedicationSelectionBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(med: MedicationResponse) {
            binding.tvName.text = med.name
            binding.tvAtc.text = med.atcCode ?: ""
            binding.checkbox.isChecked = med.id in selectedIds

            binding.checkbox.setOnCheckedChangeListener { _, isChecked ->
                onMedicationSelected(med, isChecked)
            }
            binding.root.setOnClickListener {
                binding.checkbox.isChecked = !binding.checkbox.isChecked
            }
        }
    }

    class Diff : DiffUtil.ItemCallback<MedicationResponse>() {
        override fun areItemsTheSame(old: MedicationResponse, new: MedicationResponse) =
            old.id == new.id
        override fun areContentsTheSame(old: MedicationResponse, new: MedicationResponse) =
            old == new
    }
}