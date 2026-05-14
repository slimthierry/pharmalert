package com.liksoft.pharmalert.ui.audit

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.liksoft.pharmalert.data.dto.AuditLogResponse
import com.liksoft.pharmalert.databinding.ItemAuditLogBinding
import java.text.SimpleDateFormat
import java.util.*

class AuditAdapter : ListAdapter<AuditLogResponse, AuditAdapter.VH>(Diff()) {

    private val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
    private val outputFormat = SimpleDateFormat("dd/MM/yyyy HH:mm", Locale.getDefault())

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val binding = ItemAuditLogBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return VH(binding)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        holder.bind(getItem(position))
    }

    inner class VH(private val binding: ItemAuditLogBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(log: AuditLogResponse) {
            // Action label
            val actionDisplay = formatAction(log.action)
            binding.tvAction.text = actionDisplay

            // Entity type badge
            binding.tvEntityType.text = log.entityType.replaceFirstChar { it.uppercase() }

            // Timestamp
            binding.tvTimestamp.text = formatTimestamp(log.createdAt)

            // User name
            binding.tvUserName.text = log.userName?.let { "par $it" } ?: ""

            // Details
            if (!log.details.isNullOrBlank()) {
                binding.tvDetails.text = log.details
                binding.tvDetails.visibility = View.VISIBLE
            } else {
                binding.tvDetails.visibility = View.GONE
            }
        }

        private fun formatAction(action: String): String {
            return when (action) {
                "create" -> "Creation"
                "update" -> "Modification"
                "delete" -> "Suppression"
                "login" -> "Connexion"
                "logout" -> "Deconnexion"
                "validate" -> "Validation"
                "reject" -> "Rejet"
                "record" -> "Enregistrement"
                else -> action.replaceFirstChar { it.uppercase() }
            }
        }

        private fun formatTimestamp(timestamp: String): String {
            return try {
                val date = inputFormat.parse(timestamp)
                date?.let { outputFormat.format(it) } ?: timestamp
            } catch (e: Exception) {
                timestamp.take(16)
            }
        }
    }

    class Diff : DiffUtil.ItemCallback<AuditLogResponse>() {
        override fun areItemsTheSame(old: AuditLogResponse, new: AuditLogResponse) =
            old.id == new.id
        override fun areContentsTheSame(old: AuditLogResponse, new: AuditLogResponse) =
            old == new
    }
}