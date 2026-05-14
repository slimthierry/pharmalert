package com.liksoft.pharmalert.ui.interaction

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.liksoft.pharmalert.R
import com.liksoft.pharmalert.databinding.FragmentInteractionsBinding
import com.liksoft.pharmalert.ui.adapter.InteractionAdapter

class InteractionFragment : Fragment() {

    private var _binding: FragmentInteractionsBinding? = null
    private val binding get() = _binding!!

    private val viewModel: InteractionViewModel by viewModels()
    private lateinit var adapter: InteractionAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentInteractionsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupRecyclerView()
        setupSwipeRefresh()
        setupCheckButton()
        observeViewModel()
    }

    private fun setupRecyclerView() {
        adapter = InteractionAdapter()
        binding.rvInteractions.layoutManager = LinearLayoutManager(requireContext())
        binding.rvInteractions.adapter = adapter
    }

    private fun setupSwipeRefresh() {
        binding.swipeRefresh.setColorSchemeResources(R.color.brand_600)
        binding.swipeRefresh.setOnRefreshListener { viewModel.refresh() }
    }

    private fun setupCheckButton() {
        binding.btnCheckInteraction.setOnClickListener {
            val dialog = CheckInteractionDialog.newInstance()
            dialog.show(parentFragmentManager, "check_interactions")
        }
    }

    private fun observeViewModel() {
        viewModel.uiState.observe(viewLifecycleOwner) { state ->
            binding.swipeRefresh.isRefreshing = false
            when (state) {
                is InteractionUiState.Loading -> {
                    binding.loadingIndicator.visibility = View.VISIBLE
                    binding.rvInteractions.visibility = View.GONE
                    binding.emptyState.visibility = View.GONE
                }
                is InteractionUiState.Success -> {
                    binding.loadingIndicator.visibility = View.GONE
                    binding.rvInteractions.visibility = View.VISIBLE
                    binding.emptyState.visibility = View.GONE
                    adapter.submitList(state.interactions)
                }
                is InteractionUiState.Empty -> {
                    binding.loadingIndicator.visibility = View.GONE
                    binding.rvInteractions.visibility = View.GONE
                    binding.emptyState.visibility = View.VISIBLE
                }
                is InteractionUiState.Error -> {
                    binding.loadingIndicator.visibility = View.GONE
                    Toast.makeText(requireContext(), state.message, Toast.LENGTH_LONG).show()
                }
            }
        }

        viewModel.summary.observe(viewLifecycleOwner) { summary ->
            binding.tvContraindicated.text = summary.contraindicated.toString()
            binding.tvMajor.text = summary.major.toString()
            binding.tvModerate.text = summary.moderate.toString()
            binding.tvMinor.text = summary.minor.toString()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
