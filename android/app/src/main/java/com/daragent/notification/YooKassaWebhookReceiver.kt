package com.daragent.notification

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log
import com.daragent.data.local.DarAgentDatabase
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class YooKassaWebhookReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val paymentId = intent.getStringExtra("payment_id")
        val status = intent.getStringExtra("status")
        Log.d("YooKassaWebhook", "Received webhook: payment=$paymentId status=$status")
        if (paymentId != null && status != null) {
            PaymentStatusWorker.enqueue(context, paymentId, status)
            CoroutineScope(Dispatchers.IO).launch {
                val db = DarAgentDatabase.getDatabase(context)
                val paymentDao = db.paymentDao()
                val payment = paymentDao.get(paymentId)
                if (payment != null) {
                    paymentDao.insert(payment.copy(status = status))
                }
            }
        }
    }
}
