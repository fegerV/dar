package com.daragent

import android.app.Application
import com.daragent.di.ServiceLocator
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class DarAgentApp : Application() {

    override fun onCreate() {
        super.onCreate()
        // The legacy ServiceLocator (pre-Hilt wiring) needs a context to build its Room
        // database. Handing it the context here keeps ServiceLocator from holding a static
        // reference to this Application subclass.
        ServiceLocator.init(this)
    }
}
