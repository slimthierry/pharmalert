package com.liksoft.pharmalert.ui.prescription

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.core.widget.doAfterTextChanged
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.liksoft.pharmalert.R
import com.liksoft.pharmalert.databinding.FragmentPrescriptionsBinding
import com.liksoft.pharmalert.ui.adapter.PrescriptionAdapter

class PrescriptionFragment : Fragment() {

    private var _binding: FragmentPrescriptionsBinding? = null
    private val binding get() = _binding!!

    private val viewModel: PrescriptionViewModel by viewModels()
    private lateinit var adapter: PrescriptionAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentPrescriptionsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupRecyclerView()
        setupSearch()
        setupFilters()
        setupFab()
        setupSwipeRefresh()
        observeViewModel()
    }

    private fun setupRecyclerView() {
        adapter = PrescriptionAdapter()
        binding.rvPrescriptions.layoutManager = LinearLayoutManager(requireContext())
        binding.rvPrescriptions.adapter = adapter
    }

    private fun setupSearch() {
        binding.etSearch.doAfterTextChanged { text ->
            viewModel.loadPrescriptions(
                status = getCurrentFilterStatus(),
                search = text?.toString()?.takeIf { it.isNotBlank() }
            )
        }
    }

    private fun setupFilters() {
        binding.chipGroup.setOnCheckedStateChangeListener { _, _ ->
            viewModel.loadPrescriptions(
                status = getCurrentFilterStatus(),
                search = binding.etSearch.text?.toString()?.takeIf { it.isNotBlank() }
            )
        }
    }

    private fun getCurrentFilterStatus(): String? {
        return when (binding.chipGroup.checkedChipId) {
            R.id.chipPending -> "pending"
            R.id.chipValidated -> "validated"
            R.id.chipRejected -> "rejected"
            else -> null
        }
    }

    private fun setupFab() {
        binding.fabAdd.setOnClickListener {
            val dialog = CreatePrescriptionDialog.newInstance {
                viewModel.refresh()
            }
            dialog.show(parentFragmentManager, "create_prescription")
        }
    }

    private fun setupSwipeRefresh() {
        binding.swipeRefresh.setColorSchemeResources(R.color.brand_600)
        binding.swipeRefresh.setOnRefreshListener { viewModel.refresh() }
    }

    private fun observeViewModel() {
        viewModel.uiState.observe(viewLifecycleOwner) { state ->
            binding.swipeRefresh.isRefreshing = false
            when (state) {
                is PrescriptionUiState.Loading -> {
                    binding.loadingIndicator.visibility = View.VISIBLE
                    binding.rvPrescriptions.visibility = View.GONE
                    binding.emptyState.visibility = View.GONE
                }
                is PrescriptionUiState.Success -> {
                    binding.loadingIndicator.visibility = View.GONE
                    binding.rvPrescriptions.visibility = View.VISIBLE
                    binding.emptyState.visibility = View.GONE
                    adapter.submitList(state.prescriptions)
                }
                is PrescriptionUiState.Empty -> {
                    binding.loadingIndicator.visibility = View.GONE
                    binding.rvPrescriptions.visibility = View.GONE
                    binding.emptyState.visibility = View.VISIBLE
                }
                is PrescriptionUiState.Error -> {
                    binding.loadingIndicator.visibility = View.GONE
                    Toast.makeText(requireContext(), state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
