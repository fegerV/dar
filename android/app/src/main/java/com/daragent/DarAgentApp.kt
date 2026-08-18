package com.daragent

import android.app.Application
import com.daragent.data.local.DarAgentDatabase

class DarAgentApp : Application() {
    val database by lazy { DarAgentDatabase.getDatabase(this) }
}
