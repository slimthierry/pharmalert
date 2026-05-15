package com.liksoft.pharmalert.ui

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import androidx.activity.OnBackPressedCallback
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.GravityCompat
import androidx.lifecycle.lifecycleScope
import androidx.navigation.NavController
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.AppBarConfiguration
import androidx.navigation.ui.navigateUp
import androidx.navigation.ui.setupActionBarWithNavController
import androidx.navigation.ui.setupWithNavController
import com.liksoft.pharmalert.R
import com.liksoft.pharmalert.databinding.ActivityMainBinding
import com.liksoft.pharmalert.util.EntityManager
import com.liksoft.pharmalert.util.SessionManager
import com.liksoft.pharmalert.util.TokenStorage
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var navController: NavController
    private lateinit var appBarConfiguration: AppBarConfiguration
    private lateinit var tokenStorage: TokenStorage

    private var entitySpinner: android.widget.Spinner? = null
    private var entityAdapter: ArrayAdapter<String>? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        tokenStorage = TokenStorage(this)

        setupToolbar()
        setupNavigation()
        setupNavHeader()
        setupBackPressHandler()
        loadEntities()
    }

    private fun setupToolbar() {
        setSupportActionBar(binding.toolbar)
    }

    private fun setupNavigation() {
        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.navHostFragment) as NavHostFragment
        navController = navHostFragment.navController

        appBarConfiguration = AppBarConfiguration(
            setOf(
                R.id.nav_dashboard,
                R.id.nav_prescriptions,
                R.id.nav_interactions,
                R.id.nav_administrations,
                R.id.nav_allergies
            ),
            binding.drawerLayout
        )

        setupActionBarWithNavController(navController, appBarConfiguration)
        binding.navView.setupWithNavController(navController)

        binding.navView.setNavigationItemSelectedListener { menuItem ->
            when (menuItem.itemId) {
                R.id.nav_logout -> {
                    tokenStorage.clear()
                    SessionManager.logout()
                    EntityManager.clear()
                    startActivity(Intent(this, LoginActivity::class.java))
                    finish()
                }
                else -> {
                    navController.navigate(menuItem.itemId)
                    binding.drawerLayout.closeDrawer(GravityCompat.START)
                }
            }
            true
        }
    }

    private fun setupNavHeader() {
        val header = binding.navView.getHeaderView(0)
        header.findViewById<android.widget.TextView>(R.id.tvUserName)?.text = SessionManager.userName
        header.findViewById<android.widget.TextView>(R.id.tvUserRole)?.text = SessionManager.userRole.replaceFirstChar { it.uppercase() }

        entitySpinner = header.findViewById(R.id.spEntity)
    }

    private fun loadEntities() {
        lifecycleScope.launch {
            try {
                EntityManager.loadEntitiesFromApi()
                setupEntitySpinner()
            } catch (e: Exception) {
                // If entities fail to load, just hide spinner
                entitySpinner?.visibility = View.GONE
            }
        }
    }

    private fun setupBackPressHandler() {
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (binding.drawerLayout.isDrawerOpen(GravityCompat.START)) {
                    binding.drawerLayout.closeDrawer(GravityCompat.START)
                } else {
                    isEnabled = false
                    onBackPressedDispatcher.onBackPressed()
                }
            }
        })
    }

    private fun setupEntitySpinner() {
        val entities = EntityManager.entities
        if (entities.isEmpty()) {
            entitySpinner?.visibility = View.GONE
            return
        }

        entitySpinner?.visibility = View.VISIBLE
        val entityNames = entities.map { it.name }
        entityAdapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, entityNames)
        entityAdapter?.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        entitySpinner?.adapter = entityAdapter

        // Select current entity
        EntityManager.currentEntity?.let { current ->
            val index = entities.indexOfFirst { it.id == current.id }
            if (index >= 0) entitySpinner?.setSelection(index)
        }

        entitySpinner?.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                val selected = entities[position]
                if (selected.id != EntityManager.currentEntity?.id) {
                    EntityManager.selectEntity(selected)
                }
            }
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        return navController.navigateUp(appBarConfiguration) || super.onSupportNavigateUp()
    }

}
