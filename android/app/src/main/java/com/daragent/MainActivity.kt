package com.daragent

import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.navigation.compose.rememberNavController
import com.daragent.data.local.DarAgentDatabase
import com.daragent.navigation.DarAgentNavGraph
import com.daragent.notification.NotificationHelper

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        NotificationHelper.createChannel(this)
        DarAgentDatabase.getDatabase(this)

        val deepLink = intent?.data
        if (deepLink != null && deepLink.scheme == "daragent" && deepLink.host == "yookassa") {
            val paymentId = deepLink.getQueryParameter("payment_id")
            val status = deepLink.getQueryParameter("status")
            if (paymentId != null && status != null) {
                PaymentStatusWorker.enqueue(this, paymentId, status)
            }
        }

        setContent {
            MaterialTheme(colorScheme = darkColorScheme()) {
                val navController = rememberNavController()
                val generationId = intent?.getStringExtra("generation_id")
                if (generationId != null) {
                    navController.navigate("generation_progress/$generationId")
                }
                DarAgentNavGraph(navController = navController)
            }
        }
    }
}
