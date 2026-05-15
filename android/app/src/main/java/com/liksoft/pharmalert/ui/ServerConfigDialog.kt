package com.liksoft.pharmalert.ui

import android.app.Dialog
import android.os.Bundle
import android.view.LayoutInflater
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.DialogFragment
import com.google.android.material.textfield.TextInputEditText
import com.liksoft.pharmalert.R
import com.liksoft.pharmalert.util.ServerConfig

/**
 * Dialogue de configuration du serveur API.
 * Permet de modifier l'URL du backend PharmAlert.
 *
 * Utilisation:
 *   ServerConfigDialog().show(supportFragmentManager, "server_config")
 */
class ServerConfigDialog : DialogFragment() {

    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        val inflater = LayoutInflater.from(requireContext())
        val view = inflater.inflate(R.layout.dialog_server_config, null)

        val editUrl = view.findViewById<TextInputEditText>(R.id.editServerUrl)

        // Afficher l'URL actuelle
        editUrl.setText(ServerConfig.baseUrl)

        return AlertDialog.Builder(requireContext())
            .setTitle("Configuration Serveur")
            .setView(view)
            .setPositiveButton("Enregistrer") { _, _ ->
                val newUrl = editUrl.text?.toString()?.trim() ?: ""
                if (newUrl.isNotEmpty()) {
                    ServerConfig.baseUrl = newUrl
                    Toast.makeText(
                        requireContext(),
                        "Serveur configuré: $newUrl\nRedémarrez l'application pour appliquer.",
                        Toast.LENGTH_LONG
                    ).show()
                    // Force logout so user re-authenticates with new URL
                    activity?.let {
                        com.liksoft.pharmalert.util.SessionManager.logout()
                    }
                }
            }
            .setNegativeButton("Annuler", null)
            .setNeutralButton("Réinitialiser") { _, _ ->
                ServerConfig.reset()
                Toast.makeText(requireContext(), "URL réinitialisée", Toast.LENGTH_SHORT).show()
            }
            .create()
    }

    companion object {
        const val TAG = "ServerConfigDialog"

        fun show(fragmentManager: androidx.fragment.app.FragmentManager) {
            ServerConfigDialog().show(fragmentManager, TAG)
        }
    }
}