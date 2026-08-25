package com.daragent.payment

import com.daragent.data.payment.PaymentRepository
import com.daragent.data.payment.PaymentCreationResult
import com.daragent.domain.payment.CreatePaymentUseCase
import com.daragent.domain.payment.GetPaymentStatusUseCase
import com.daragent.domain.payment.GetPaymentsUseCase
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mock
import org.mockito.junit.MockitoJUnitRunner

@RunWith(MockitoJUnitRunner::class)
class PaymentUseCasesTest {

    @Mock
    private lateinit var paymentRepository: PaymentRepository
    private lateinit var createPaymentUseCase: CreatePaymentUseCase
    private lateinit var getPaymentStatusUseCase: GetPaymentStatusUseCase
    private lateinit var getPaymentsUseCase: GetPaymentsUseCase

    @Before
    fun setup() {
        createPaymentUseCase = CreatePaymentUseCase(paymentRepository)
        getPaymentStatusUseCase = GetPaymentStatusUseCase(paymentRepository)
        getPaymentsUseCase = GetPaymentsUseCase(paymentRepository)
    }

    @Test
    fun `CreatePaymentUseCase should call repository with correct parameters`() = runTest {
        val mockResult = PaymentCreationResult(
            id = "pay_123",
            confirmationUrl = "https://yookassa.ru/pay/123"
        )
        `when`(paymentRepository.createPayment(499.0, "RUB"))
            .thenReturn(Result.success(mockResult))

        val result = createPaymentUseCase(499.0, "RUB")

        assertTrue(result.isSuccess)
        assertEquals("pay_123", result.getOrNull()?.id)
    }

    @Test
    fun `CreatePaymentUseCase should propagate failure`() = runTest {
        val exception = RuntimeException("Network error")
        `when`(paymentRepository.createPayment(499.0, "RUB"))
            .thenReturn(Result.failure(exception))

        val result = createPaymentUseCase(499.0, "RUB")

        assertTrue(result.isFailure)
    }

    @Test
    fun `GetPaymentStatusUseCase should return payment when found`() = runTest {
        val mockPayment = com.daragent.core.network.model.PaymentDto(
            id = "pay_123",
            amount = 499.0,
            status = "succeeded",
            createdAt = "2026-08-26T00:00:00Z"
        )
        `when`(paymentRepository.getPayment("pay_123"))
            .thenReturn(Result.success(mockPayment))

        val result = getPaymentStatusUseCase("pay_123")

        assertTrue(result.isSuccess)
        assertEquals("succeeded", result.getOrNull()?.status)
    }

    @Test
    fun `GetPaymentsUseCase should return list of payments`() = runTest {
        val mockPayments = listOf(
            com.daragent.core.network.model.PaymentDto(
                id = "pay_123",
                amount = 499.0,
                status = "succeeded",
                createdAt = "2026-08-26T00:00:00Z"
            ),
            com.daragent.core.network.model.PaymentDto(
                id = "pay_456",
                amount = 999.0,
                status = "pending",
                createdAt = "2026-08-25T00:00:00Z"
            )
        )
        `when`(paymentRepository.getPayments())
            .thenReturn(Result.success(mockPayments))

        val result = getPaymentsUseCase()

        assertTrue(result.isSuccess)
        assertEquals(2, result.getOrNull()?.size)
    }

    @Test
    fun `GetPaymentsUseCase should propagate failure`() = runTest {
        val exception = RuntimeException("Network error")
        `when`(paymentRepository.getPayments())
            .thenReturn(Result.failure(exception))

        val result = getPaymentsUseCase()

        assertTrue(result.isFailure)
    }
}
