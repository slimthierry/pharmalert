package com.liksoft.pharmalert.ui.allergy

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
import com.liksoft.pharmalert.databinding.FragmentAllergiesBinding
import com.liksoft.pharmalert.ui.adapter.AllergyAdapter

class AllergyFragment : Fragment() {

    private var _binding: FragmentAllergiesBinding? = null
    private val binding get() = _binding!!

    private val viewModel: AllergyViewModel by viewModels()
    private lateinit var adapter: AllergyAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentAllergiesBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupRecyclerView()
        setupSearch()
        setupFab()
        setupSwipeRefresh()
        observeViewModel()
    }

    private fun setupRecyclerView() {
        adapter = AllergyAdapter()
        binding.rvAllergies.layoutManager = LinearLayoutManager(requireContext())
        binding.rvAllergies.adapter = adapter
    }

    private fun setupSearch() {
        binding.etSearch.doAfterTextChanged { text ->
            viewModel.loadAllergies(
                patientIpp = text?.toString()?.takeIf { it.isNotBlank() }
            )
        }
    }

    private fun setupFab() {
        binding.fabAdd.setOnClickListener {
            val dialog = CreateAllergyDialog.newInstance {
                viewModel.refresh()
            }
            dialog.show(parentFragmentManager, "create_allergy")
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
                is AllergyUiState.Loading -> {
                    binding.loadingIndicator.visibility = View.VISIBLE
                    binding.rvAllergies.visibility = View.GONE
                    binding.emptyState.visibility = View.GONE
                }
                is AllergyUiState.Success -> {
                    binding.loadingIndicator.visibility = View.GONE
                    binding.rvAllergies.visibility = View.VISIBLE
                    binding.emptyState.visibility = View.GONE
                    adapter.submitList(state.allergies)
                }
                is AllergyUiState.Empty -> {
                    binding.loadingIndicator.visibility = View.GONE
                    binding.rvAllergies.visibility = View.GONE
                    binding.emptyState.visibility = View.VISIBLE
                }
                is AllergyUiState.Error -> {
                    binding.loadingIndicator.visibility = View.GONE
                    Toast.makeText(requireContext(), state.message, Toast.LENGTH_LONG).show()
                }
            }
        }

        viewModel.summary.observe(viewLifecycleOwner) { summary ->
            binding.tvLifeThreatening.text = summary.lifeThreatening.toString()
            binding.tvSevere.text = summary.severe.toString()
            binding.tvConfirmed.text = summary.confirmed.toString()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
