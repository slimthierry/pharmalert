package com.liksoft.pharmalert.ui

import android.content.Intent
import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.liksoft.pharmalert.data.dto.UserResponse
import com.liksoft.pharmalert.databinding.ActivityLoginBinding
import com.liksoft.pharmalert.util.SessionManager
import com.liksoft.pharmalert.util.TokenStorage
import io.ktor.client.plugins.*
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json

class LoginActivity : AppCompatActivity() {

    private lateinit var binding: ActivityLoginBinding
    private lateinit var tokenStorage: TokenStorage

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)

        tokenStorage = TokenStorage(this)

        if (tokenStorage.isLoggedIn()) {
            SessionManager.api.setToken(tokenStorage.getToken())
            navigateToMain()
            return
        }

        setupListeners()
    }

    private fun setupListeners() {
        binding.btnLogin.setOnClickListener {
            val email = binding.etEmail.text.toString().trim()
            val password = binding.etPassword.text.toString()

            if (email.isEmpty()) {
                binding.tilEmail.error = "Email requis"
                return@setOnClickListener
            }
            binding.tilEmail.error = null

            if (password.isEmpty()) {
                binding.tilPassword.error = "Mot de passe requis"
                return@setOnClickListener
            }
            binding.tilPassword.error = null

            login(email, password)
        }
    }

    private fun login(email: String, password: String) {
        setLoading(true)
        lifecycleScope.launch {
            try {
                val response = SessionManager.api.login(email, password)
                tokenStorage.saveToken(response.accessToken)

                val user = UserResponse(
                    id = response.userId ?: 0,
                    email = response.email,
                    name = response.name,
                    role = response.role
                )
                SessionManager.login(response.accessToken, user)
                // Load entities for multi-entity support
                com.liksoft.pharmalert.util.EntityManager.loadEntitiesFromApi()
                navigateToMain()
            } catch (e: Exception) {
                setLoading(false)
                val message = when {
                    e is HttpRequestTimeoutException -> "Delai d'attente depasse"
                    else -> "Erreur de connexion: ${e.localizedMessage}"
                }
                binding.tvError.text = message
                binding.tvError.visibility = View.VISIBLE
            }
        }
    }

    private fun setLoading(loading: Boolean) {
        binding.progressBar.visibility = if (loading) View.VISIBLE else View.GONE
        binding.btnLogin.isEnabled = !loading
        binding.etEmail.isEnabled = !loading
        binding.etPassword.isEnabled = !loading
    }

    private fun navigateToMain() {
        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }
}
