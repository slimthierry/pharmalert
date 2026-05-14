package com.liksoft.pharmalert.ui.administration

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.liksoft.pharmalert.R
import com.liksoft.pharmalert.data.dto.AdministrationResponse
import com.liksoft.pharmalert.databinding.FragmentAdministrationsBinding
import com.liksoft.pharmalert.ui.adapter.AdministrationAdapter

class AdministrationFragment : Fragment() {

    private var _binding: FragmentAdministrationsBinding? = null
    private val binding get() = _binding!!

    private val viewModel: AdministrationViewModel by viewModels()
    private lateinit var adapter: AdministrationAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentAdministrationsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupRecyclerView()
        setupFilters()
        setupSwipeRefresh()
        observeViewModel()
    }

    private fun setupRecyclerView() {
        adapter = AdministrationAdapter { administration ->
            showRecordDialog(administration)
        }
        binding.rvAdministrations.layoutManager = LinearLayoutManager(requireContext())
        binding.rvAdministrations.adapter = adapter
    }

    private fun setupFilters() {
        binding.chipGroup.setOnCheckedStateChangeListener { _, checkedIds ->
            val status = when {
                checkedIds.contains(R.id.chipPending) -> "pending"
                checkedIds.contains(R.id.chipGiven) -> "given"
                checkedIds.contains(R.id.chipRefused) -> "refused"
                else -> null
            }
            viewModel.loadAdministrations(status)
        }
    }

    private fun setupSwipeRefresh() {
        binding.swipeRefresh.setColorSchemeResources(R.color.brand_600)
        binding.swipeRefresh.setOnRefreshListener { viewModel.refresh() }
    }

    private fun showRecordDialog(administration: AdministrationResponse) {
        val options = arrayOf("Donne", "Refuse", "Retarde", "Oubli")
        MaterialAlertDialogBuilder(requireContext())
            .setTitle("Enregistrer l'administration")
            .setItems(options) { _, which ->
                val status = when (which) {
                    0 -> "given"
                    1 -> "refused"
                    2 -> "delayed"
                    3 -> "missed"
                    else -> "given"
                }
                viewModel.recordAdministration(administration.id, status, null, null)
            }
            .show()
    }

    private fun observeViewModel() {
        viewModel.uiState.observe(viewLifecycleOwner) { state ->
            binding.swipeRefresh.isRefreshing = false
            when (state) {
                is AdministrationUiState.Loading -> {
                    binding.loadingIndicator.visibility = View.VISIBLE
                    binding.rvAdministrations.visibility = View.GONE
                    binding.emptyState.visibility = View.GONE
                }
                is AdministrationUiState.Success -> {
                    binding.loadingIndicator.visibility = View.GONE
                    binding.rvAdministrations.visibility = View.VISIBLE
                    binding.emptyState.visibility = View.GONE
                    adapter.submitList(state.administrations)
                    updateSummary(state.administrations)
                }
                is AdministrationUiState.Empty -> {
                    binding.loadingIndicator.visibility = View.GONE
                    binding.rvAdministrations.visibility = View.GONE
                    binding.emptyState.visibility = View.VISIBLE
                }
                is AdministrationUiState.Error -> {
                    binding.loadingIndicator.visibility = View.GONE
                    Toast.makeText(requireContext(), state.message, Toast.LENGTH_LONG).show()
                }
            }
        }

        viewModel.recordResult.observe(viewLifecycleOwner) { result ->
            when (result) {
                is RecordResult.Success -> {
                    Toast.makeText(requireContext(), "Enregistre avec succes", Toast.LENGTH_SHORT).show()
                    viewModel.clearRecordResult()
                }
                is RecordResult.Error -> {
                    Toast.makeText(requireContext(), result.message, Toast.LENGTH_LONG).show()
                    viewModel.clearRecordResult()
                }
                null -> {}
            }
        }
    }

    private fun updateSummary(list: List<AdministrationResponse>) {
        binding.tvTotalToday.text = list.size.toString()
        binding.tvPending.text = list.count { it.status == "pending" || it.status == "delayed" }.toString()
        binding.tvGiven.text = list.count { it.status == "given" }.toString()
        binding.tvRefused.text = list.count { it.status == "refused" || it.status == "missed" }.toString()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
