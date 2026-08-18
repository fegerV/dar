package com.daragent.data.repository

import com.daragent.data.network.api.PaymentsApi
import com.daragent.data.network.dto.ConsumeEntitlementRequest
import com.daragent.data.network.dto.EntitlementResponse
import com.daragent.data.network.dto.PaymentCreateRequest
import com.daragent.data.network.dto.PaymentResponse
import com.daragent.data.network.dto.WalletResponse
import com.daragent.domain.model.Entitlement
import com.daragent.domain.model.Payment
import com.daragent.domain.model.Wallet
import com.daragent.domain.repository.PaymentRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class PaymentRepositoryImpl(private val api: PaymentsApi) : PaymentRepository {
    override suspend fun createPayment(projectId: String, method: String): Result<Payment> =
        withContext(Dispatchers.IO) {
            runCatching {
                api.create(projectId, PaymentCreateRequest(method)).body()!!.toDomain()
            }
        }

    override suspend fun getPayment(paymentId: String): Result<Payment> =
        withContext(Dispatchers.IO) {
            runCatching { api.get(paymentId).body()!!.toDomain() }
        }

    override suspend fun wallet(): Result<Wallet> =
        withContext(Dispatchers.IO) {
            runCatching { api.wallet().body()!!.toDomain() }
        }

    override suspend fun listEntitlements(): Result<List<Entitlement>> =
        withContext(Dispatchers.IO) {
            runCatching { api.entitlements().body().orEmpty().map { it.toDomain() } }
        }

    override suspend fun consumeEntitlement(entitlementId: String): Result<Entitlement> =
        withContext(Dispatchers.IO) {
            runCatching { api.consumeEntitlement(entitlementId).body()!!.toDomain() }
        }
}

private fun PaymentResponse.toDomain() = Payment(
    id = id,
    projectId = project_id,
    amount = amount_rub,
    status = status,
    method = method,
    confirmationUrl = confirmation_url,
    createdAt = created_at,
    paidAt = paid_at
)

private fun WalletResponse.toDomain() = Wallet(
    userId = user_id,
    balanceRub = balance_rub,
    bonusBalance = bonus_balance,
    updatedAt = null
)

private fun EntitlementResponse.toDomain() = Entitlement(
    id = id,
    userId = "",
    code = code,
    quantity = quantity,
    consumed = consumed,
    expiresAt = expires_at,
    source = source,
    createdAt = created_at
)
