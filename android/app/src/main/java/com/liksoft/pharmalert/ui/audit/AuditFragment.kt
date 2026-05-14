package com.liksoft.pharmalert.ui.audit

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.liksoft.pharmalert.R
import com.liksoft.pharmalert.databinding.FragmentAuditBinding

class AuditFragment : Fragment() {

    private var _binding: FragmentAuditBinding? = null
    private val binding get() = _binding!!

    private val viewModel: AuditViewModel by viewModels()
    private lateinit var adapter: AuditAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentAuditBinding.inflate(inflater, container, false)
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
        adapter = AuditAdapter()
        binding.rvAudit.layoutManager = LinearLayoutManager(requireContext())
        binding.rvAudit.adapter = adapter
    }

    private fun setupFilters() {
        binding.chipGroup.setOnCheckedStateChangeListener { _, checkedIds ->
            val (action, entityType) = when {
                checkedIds.contains(R.id.chipCreate) -> "create" to null
                checkedIds.contains(R.id.chipUpdate) -> "update" to null
                checkedIds.contains(R.id.chipLogin) -> "login" to null
                else -> null to null
            }
            viewModel.loadLogs(action = action, entityType = entityType)
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
                is AuditUiState.Loading -> {
                    binding.loadingIndicator.visibility = View.VISIBLE
                    binding.rvAudit.visibility = View.GONE
                    binding.emptyState.visibility = View.GONE
                }
                is AuditUiState.Success -> {
                    binding.loadingIndicator.visibility = View.GONE
                    binding.rvAudit.visibility = View.VISIBLE
                    binding.emptyState.visibility = View.GONE
                    adapter.submitList(state.logs)
                }
                is AuditUiState.Empty -> {
                    binding.loadingIndicator.visibility = View.GONE
                    binding.rvAudit.visibility = View.GONE
                    binding.emptyState.visibility = View.VISIBLE
                }
                is AuditUiState.Error -> {
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