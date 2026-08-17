package com.daragent.domain.repository

import com.daragent.domain.model.Entitlement
import com.daragent.domain.model.Payment
import com.daragent.domain.model.Wallet

interface PaymentRepository {
    suspend fun createPayment(projectId: String, method: String): Result<Payment>
    suspend fun getPayment(paymentId: String): Result<Payment>
    suspend fun wallet(): Result<Wallet>
    suspend fun listEntitlements(): Result<List<Entitlement>>
    suspend fun consumeEntitlement(entitlementId: String): Result<Entitlement>
}
