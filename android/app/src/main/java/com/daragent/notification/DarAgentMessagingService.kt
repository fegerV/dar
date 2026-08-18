package com.daragent.notification

import android.util.Log
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage

class DarAgentMessagingService : FirebaseMessagingService() {
    override fun onNewToken(token: String) {
        super.onNewToken(token)
        Log.d("FCM", "New token: $token")
    }

    override fun onMessageReceived(message: RemoteMessage) {
        super.onMessageReceived(message)
        val title = message.notification?.title ?: "DarAgent"
        val body = message.notification?.body ?: ""
        val generationId = message.data["generation_id"] ?: ""

        NotificationHelper.createChannel(this)
        NotificationHelper.showVideoReadyNotification(this, title, body, generationId)
    }
}
