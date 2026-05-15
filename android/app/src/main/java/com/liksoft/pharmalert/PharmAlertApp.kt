package com.liksoft.pharmalert

import android.app.Application
import com.liksoft.pharmalert.util.EntityManager

class PharmAlertApp : Application() {
    override fun onCreate() {
        super.onCreate()
        instance = this
        EntityManager.init(this)
    }

    companion object {
        lateinit var instance: PharmAlertApp
            private set
    }
}