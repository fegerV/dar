package com.daragent

import android.app.Application
import com.daragent.data.local.DatabaseModule

class DarAgentApp : Application() {
    val database by lazy { DatabaseModule.provideDatabase(this) }
}
