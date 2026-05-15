package com.liksoft.pharmalert.util

import android.content.Context
import android.content.SharedPreferences

/**
 * Gère la configuration du serveur (URL de l'API).
 * Les valeurs sont stockées dans SharedPreferences pour persistance.
 *
 * Par défaut: http://10.0.2.2:9600/api/v1/ (émulateur Android)
 * Pour iPhone sur le même réseau: utiliser http://IP_LOCAL:9600/api/v1/
 */
object ServerConfig {

    private const val PREFS_NAME = "pharmalert_server_prefs"
    private const val KEY_BASE_URL = "api_base_url"
    private const val DEFAULT_URL = "http://10.0.2.2:9600/api/v1/"

    private lateinit var prefs: SharedPreferences

    fun init(context: Context) {
        prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    }

    var baseUrl: String
        get() = prefs.getString(KEY_BASE_URL, DEFAULT_URL) ?: DEFAULT_URL
        set(value) {
            // Ensure trailing slash
            val normalizedUrl = if (value.endsWith("/")) value else "$value/"
            prefs.edit().putString(KEY_BASE_URL, normalizedUrl).apply()
        }

    val isCustomUrl: Boolean
        get() = baseUrl != DEFAULT_URL

    fun reset() {
        baseUrl = DEFAULT_URL
    }

    fun getFullUrl(path: String): String {
        val cleanPath = if (path.startsWith("/")) path else "/$path"
        return baseUrl.trimEnd('/') + cleanPath
    }
}