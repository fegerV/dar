package com.daragent.payment

import com.daragent.domain.model.Payment
import com.daragent.domain.payment.CreatePaymentUseCase
import com.daragent.domain.payment.GetPaymentStatusUseCase
import com.daragent.domain.repository.PaymentRepository
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mock
import org.mockito.junit.MockitoJUnitRunner
import org.mockito.kotlin.whenever

/**
 * Covers the domain-level payment use cases against the domain PaymentRepository.
 *
 * There is deliberately no list-payments use case: the backend exposes payments only under
 * /admin/payments (see backend/app/api/v1/payments.py), so no user-facing list endpoint exists
 * to back one.
 */
@RunWith(MockitoJUnitRunner::class)
class PaymentUseCasesTest {

    @Mock
    private lateinit var paymentRepository: PaymentRepository

    private lateinit var createPaymentUseCase: CreatePaymentUseCase
    private lateinit var getPaymentStatusUseCase: GetPaymentStatusUseCase

    @Before
    fun setup() {
        createPaymentUseCase = CreatePaymentUseCase(paymentRepository)
        getPaymentStatusUseCase = GetPaymentStatusUseCase(paymentRepository)
    }

    @Test
    fun `CreatePaymentUseCase should forward projectId and default method`() = runTest {
        whenever(paymentRepository.createPayment("proj_1", "yookassa"))
            .thenReturn(Result.success(Payment(id = "pay_123", projectId = "proj_1")))

        val result = createPaymentUseCase(projectId = "proj_1")

        assertTrue(result.isSuccess)
        assertEquals("pay_123", result.getOrNull()?.id)
        assertEquals("proj_1", result.getOrNull()?.projectId)
    }

    @Test
    fun `CreatePaymentUseCase should forward an explicit method`() = runTest {
        whenever(paymentRepository.createPayment("proj_1", "sbp"))
            .thenReturn(Result.success(Payment(id = "pay_456", projectId = "proj_1", method = "sbp")))

        val result = createPaymentUseCase(projectId = "proj_1", method = "sbp")

        assertTrue(result.isSuccess)
        assertEquals("sbp", result.getOrNull()?.method)
    }

    @Test
    fun `CreatePaymentUseCase should propagate failure`() = runTest {
        whenever(paymentRepository.createPayment("proj_1", "yookassa"))
            .thenReturn(Result.failure(RuntimeException("Network error")))

        val result = createPaymentUseCase(projectId = "proj_1")

        assertTrue(result.isFailure)
    }

    @Test
    fun `GetPaymentStatusUseCase should return payment when found`() = runTest {
        whenever(paymentRepository.getPaymentStatus("pay_123"))
            .thenReturn(Result.success(Payment(id = "pay_123", status = "succeeded")))

        val result = getPaymentStatusUseCase("pay_123")

        assertTrue(result.isSuccess)
        assertEquals("succeeded", result.getOrNull()?.status)
    }

    @Test
    fun `GetPaymentStatusUseCase should propagate failure`() = runTest {
        whenever(paymentRepository.getPaymentStatus("missing"))
            .thenReturn(Result.failure(RuntimeException("Not found")))

        val result = getPaymentStatusUseCase("missing")

        assertTrue(result.isFailure)
    }
}
