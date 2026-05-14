package com.liksoft.pharmalert

import android.app.Application

class PharmAlertApp : Application() {
    override fun onCreate() {
        super.onCreate()
        instance = this
    }

    companion object {
        lateinit var instance: PharmAlertApp
            private set
    }
}