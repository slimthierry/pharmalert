package com.liksoft.pharmalert.util

import android.content.Context
import com.liksoft.pharmalert.data.api.PharmAlertApi
import com.liksoft.pharmalert.data.api.ApiClient
import com.liksoft.pharmalert.data.dto.UserResponse

/**
 * Gère la session utilisateur et l'API PharmAlert.
 * L'URL du serveur est configurable via ServerConfig.
 */
object SessionManager {

    private var _token: String? = null
    private var _user: UserResponse? = null
    private var _api: PharmAlertApi? = null

    /**
     * API PharmAlert — utilise ServerConfig.baseUrl (modifiable par l'utilisateur).
     * Re-créée à chaque appel pour prendre en compte les changements d'URL.
     */
    val api: PharmAlertApi by lazy {
        PharmAlertApi(ApiClient.httpClient, ServerConfig.baseUrl).also {
            _token?.let { t -> it.setToken(t) }
        }
    }

    fun login(token: String, user: UserResponse) {
        _token = token
        _user = user
        _api = null  // Reset cached API so it uses new baseUrl
        api.setToken(token)
    }

    fun logout() {
        _token = null
        _user = null
        _api = null
    }

    val isLoggedIn: Boolean get() = _token != null
    val user: UserResponse? get() = _user
    val userName: String get() = _user?.name ?: "Utilisateur"
    val userRole: String get() = _user?.role ?: ""
}