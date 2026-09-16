package com.daragent

import android.app.Application
import com.daragent.data.local.DarAgentDatabase
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class DarAgentApp : Application() {

    /** Room database, exposed for the legacy ServiceLocator wiring. */
    val database: DarAgentDatabase by lazy { DarAgentDatabase.getDatabase(this) }
}
