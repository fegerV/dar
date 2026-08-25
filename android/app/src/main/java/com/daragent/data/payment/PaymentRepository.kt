package com.daragent.data.payment

import com.daragent.core.network.api.PaymentApi
import com.daragent.core.network.model.CreatePaymentRequest
import com.daragent.core.network.model.PaymentDto
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class PaymentRepository @Inject constructor(
    private val paymentApi: PaymentApi,
) {
    suspend fun createPayment(amount: Double, currency: String): Result<PaymentCreationResult> {
        return runCatching {
            val request = CreatePaymentRequest(amount = amount, currency = currency)
            val response = paymentApi.createPayment(request)
            if (response.isSuccessful) {
                val body = response.body() ?: throw Exception("Empty response body")
                PaymentCreationResult(
                    id = body.paymentId,
                    confirmationUrl = body.confirmationUrl,
                )
            } else {
                throw Exception("Failed to create payment: ${response.code()}")
            }
        }
    }

    suspend fun getPayment(paymentId: String): Result<PaymentDto> {
        return runCatching {
            val response = paymentApi.getPayment(paymentId)
            if (response.isSuccessful) {
                response.body() ?: throw Exception("Empty response body")
            } else {
                throw Exception("Failed to get payment: ${response.code()}")
            }
        }
    }

    suspend fun getPayments(): Result<List<PaymentDto>> {
        return runCatching {
            val response = paymentApi.getPayments()
            if (response.isSuccessful) {
                response.body() ?: emptyList()
            } else {
                throw Exception("Failed to get payments: ${response.code()}")
            }
        }
    }
}

data class PaymentCreationResult(
    val id: String,
    val confirmationUrl: String?,
)
