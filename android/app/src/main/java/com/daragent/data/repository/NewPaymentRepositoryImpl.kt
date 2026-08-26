package com.daragent.data.repository

import com.daragent.core.network.PaymentApi
import com.daragent.core.network.model.CreatePaymentRequest
import com.daragent.domain.model.Payment
import com.daragent.domain.repository.PaymentRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class PaymentRepositoryImpl(
    private val paymentApi: PaymentApi,
) : PaymentRepository {

    override suspend fun createPayment(projectId: String, method: String): Result<Payment> =
        withContext(Dispatchers.IO) {
            runCatching {
                val response = paymentApi.createPayment(
                    CreatePaymentRequest(projectId = projectId, method = method)
                )
                if (response.isSuccessful) {
                    response.body()!!.toDomain()
                } else {
                    throw Exception("Failed to create payment: ${response.code()}")
                }
            }
        }

    override suspend fun getPaymentStatus(paymentId: String): Result<Payment> =
        withContext(Dispatchers.IO) {
            runCatching {
                val response = paymentApi.getPayment(paymentId)
                if (response.isSuccessful) {
                    response.body()!!.toDomain()
                } else {
                    throw Exception("Failed to get payment: ${response.code()}")
                }
            }
        }

    override suspend fun listPayments(): Result<List<Payment>> =
        withContext(Dispatchers.IO) {
            runCatching {
                val response = paymentApi.getPayments()
                if (response.isSuccessful) {
                    response.body().orEmpty().map { it.toDomain() }
                } else {
                    throw Exception("Failed to list payments: ${response.code()}")
                }
            }
        }

    private fun com.daragent.core.network.model.PaymentDto.toDomain() = Payment(
        id = id,
        userId = user_id,
        projectId = project_id,
        amount = amount_rub,
        status = status,
        method = method,
        confirmationUrl = confirmation_url,
        createdAt = created_at,
        paidAt = paid_at
    )
}
