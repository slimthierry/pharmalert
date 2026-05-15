package com.liksoft.pharmalert.ui.dashboard

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.liksoft.pharmalert.R
import com.liksoft.pharmalert.data.dto.DashboardResponse
import com.liksoft.pharmalert.databinding.FragmentDashboardBinding
import com.liksoft.pharmalert.util.SessionManager

class DashboardFragment : Fragment() {

    private var _binding: FragmentDashboardBinding? = null
    private val binding get() = _binding!!

    private val viewModel: DashboardViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentDashboardBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.swipeRefresh.setColorSchemeResources(R.color.brand_600)
        binding.swipeRefresh.setOnRefreshListener {
            viewModel.refresh()
        }

        observeViewModel()
    }

    private fun observeViewModel() {
        viewModel.uiState.observe(viewLifecycleOwner) { state ->
            binding.swipeRefresh.isRefreshing = false
            when (state) {
                is DashboardUiState.Loading -> {
                    binding.loadingIndicator.visibility = View.VISIBLE
                }
                is DashboardUiState.Success -> {
                    binding.loadingIndicator.visibility = View.GONE
                    displayDashboard(state.data)
                }
                is DashboardUiState.Error -> {
                    binding.loadingIndicator.visibility = View.GONE
                    Toast.makeText(requireContext(), state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    private fun displayDashboard(data: DashboardResponse) {
        val stats = data.stats

        binding.tvWelcome.text = getString(R.string.dashboard_welcome, getUserName())

        // Stat cards
        setStatCard(binding.cardPendingRx.root, stats.pendingValidations.toString(),
            getString(R.string.dashboard_pending_rx))
        setStatCard(binding.cardPendingAdm.root, stats.missedDosesToday.toString(),
            getString(R.string.dashboard_pending_adm))
        setStatCard(binding.cardInteractions.root, stats.criticalInteractions.toString(),
            getString(R.string.dashboard_active_inter))
        setStatCard(binding.cardTodayAdm.root, stats.totalActivePrescriptions.toString(),
            getString(R.string.dashboard_today_adm))

        // Progress (compliance rate)
        binding.tvCompleted.text = "${stats.complianceRate.toInt()}%"
        binding.progressBar.progress = stats.complianceRate.toInt()

        // Refused count - show as percentage complement
        val refusedRate = (100 - stats.complianceRate.toInt()).coerceAtLeast(0)
        binding.tvRefused.text = "$refusedRate%"

        // Alert card
        if (stats.criticalInteractions > 0) {
            binding.cardAlert.visibility = View.VISIBLE
            binding.tvAlert.text = "${stats.criticalInteractions} interaction(s) critique(s) a traiter"
        } else {
            binding.cardAlert.visibility = View.GONE
        }
    }

    private fun setStatCard(root: View, value: String, label: String) {
        root.findViewById<TextView>(R.id.tvStatValue).text = value
        root.findViewById<TextView>(R.id.tvStatLabel).text = label
    }

    private fun getUserName(): String = SessionManager.userName

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}