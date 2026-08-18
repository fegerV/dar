package com.daragent

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.navigation.compose.rememberNavController
import com.daragent.data.local.AuthTokenManager
import com.daragent.data.local.DarAgentDatabase
import com.daragent.presentation.home.MainScreen
import com.daragent.notification.NotificationHelper

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        installSplashScreen()
        NotificationHelper.createChannel(this)
        AuthTokenManager.init(this)
        DarAgentDatabase.getDatabase(this)

        val deepLink = intent?.data
        if (deepLink != null && deepLink.scheme == "daragent" && deepLink.host == "yookassa") {
            val paymentId = deepLink.getQueryParameter("payment_id")
            val status = deepLink.getQueryParameter("status")
            if (paymentId != null && status != null) {
                com.daragent.notification.PaymentStatusWorker.enqueue(this, paymentId, status)
            }
        }

        setContent {
            androidx.compose.material3.MaterialTheme {
                val navController = rememberNavController()
                val generationId = intent?.getStringExtra("generation_id")
                if (generationId != null) {
                    navController.navigate("generation_progress/$generationId")
                }
                MainScreen(navController = navController)
            }
        }
    }
}
