package com.liksoft.pharmalert.util

import com.liksoft.pharmalert.BuildConfig
import com.liksoft.pharmalert.data.api.PharmAlertApi
import com.liksoft.pharmalert.data.api.ApiClient
import com.liksoft.pharmalert.data.dto.UserResponse
import kotlinx.serialization.json.Json

object SessionManager {

    private var _token: String? = null
    private var _user: UserResponse? = null

    val api: PharmAlertApi by lazy {
        PharmAlertApi(ApiClient.httpClient, BuildConfig.API_BASE_URL).also {
            _token?.let { t -> it.setToken(t) }
        }
    }

    fun login(token: String, user: UserResponse) {
        _token = token
        _user = user
        api.setToken(token)
    }

    fun logout() {
        _token = null
        _user = null
        api.setToken(null)
    }

    val isLoggedIn: Boolean get() = _token != null
    val user: UserResponse? get() = _user
    val userName: String get() = _user?.name ?: "Utilisateur"
    val userRole: String get() = _user?.role ?: ""
}
