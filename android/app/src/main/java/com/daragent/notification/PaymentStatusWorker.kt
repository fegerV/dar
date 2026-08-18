package com.daragent.notification

import android.content.Context
import android.content.Intent
import android.util.Log
import androidx.work.Worker
import androidx.work.WorkerParameters
import com.daragent.data.local.DarAgentDatabase
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class PaymentStatusWorker(
    context: Context,
    params: WorkerParameters
) : Worker(context, params) {
    override fun doWork(): Result {
        val paymentId = inputData.getString("payment_id") ?: return Result.failure()
        val status = inputData.getString("status") ?: return Result.failure()

        Log.d("PaymentStatusWorker", "Payment $paymentId status: $status")

        CoroutineScope(Dispatchers.IO).launch {
            val db = DarAgentDatabase.getDatabase(applicationContext)
            val paymentDao = db.paymentDao()
            val payment = paymentDao.get(paymentId)
            if (payment != null) {
                paymentDao.insert(payment.copy(status = status))
            }
        }

        if (status == "paid") {
            NotificationHelper.createChannel(applicationContext)
            NotificationHelper.showVideoReadyNotification(
                applicationContext,
                "Оплата прошла",
                "Генерация видео началась",
                paymentId
            )
        }

        return Result.success()
    }

    companion object {
        fun enqueue(context: Context, paymentId: String, status: String) {
            val data = androidx.work.Data.Builder()
                .putString("payment_id", paymentId)
                .putString("status", status)
                .build()
            androidx.work.OneTimeWorkRequestBuilder<PaymentStatusWorker>()
                .setInputData(data)
                .build()
                .also { androidx.work.WorkManager.getInstance(context).enqueue(it) }
        }
    }
}
