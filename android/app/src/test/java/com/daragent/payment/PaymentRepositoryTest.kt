package com.daragent.payment

import com.daragent.core.network.api.PaymentApi
import com.daragent.core.network.model.CreatePaymentRequest
import com.daragent.core.network.model.PaymentResponse
import com.daragent.data.payment.PaymentRepository
import com.daragent.data.payment.PaymentCreationResult
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mock
import org.mockito.junit.MockitoJUnitRunner
import retrofit2.Response

@RunWith(MockitoJUnitRunner::class)
class PaymentRepositoryTest {

    @Mock
    private lateinit var paymentApi: PaymentApi
    private lateinit var paymentRepository: PaymentRepository

    @Before
    fun setup() {
        paymentRepository = PaymentRepository(paymentApi)
    }

    @Test
    fun `createPayment should return success when API call succeeds`() = runTest {
        val mockResponse = PaymentResponse(
            paymentId = "pay_123",
            confirmationUrl = "https://yookassa.ru/pay/123"
        )
        `when`(paymentApi.createPayment(any()))
            .thenReturn(Response.success(mockResponse))

        val result = paymentRepository.createPayment(499.0, "RUB")

        assertTrue(result.isSuccess)
        assertEquals("pay_123", result.getOrNull()?.id)
        assertEquals("https://yookassa.ru/pay/123", result.getOrNull()?.confirmationUrl)
    }

    @Test
    fun `createPayment should return failure when API call fails`() = runTest {
        `when`(paymentApi.createPayment(any()))
            .thenReturn(Response.error(500, okhttp3.ResponseBody.create(null, "Error")))

        val result = paymentRepository.createPayment(499.0, "RUB")

        assertTrue(result.isFailure)
    }

    @Test
    fun `getPayment should return payment when API call succeeds`() = runTest {
        val mockPayment = com.daragent.core.network.model.PaymentDto(
            id = "pay_123",
            amount = 499.0,
            status = "succeeded",
            createdAt = "2026-08-26T00:00:00Z"
        )
        `when`(paymentApi.getPayment("pay_123"))
            .thenReturn(Response.success(mockPayment))

        val result = paymentRepository.getPayment("pay_123")

        assertTrue(result.isSuccess)
        assertEquals("pay_123", result.getOrNull()?.id)
        assertEquals("succeeded", result.getOrNull()?.status)
    }

    @Test
    fun `getPayments should return list when API call succeeds`() = runTest {
        val mockPayments = listOf(
            com.daragent.core.network.model.PaymentDto(
                id = "pay_123",
                amount = 499.0,
                status = "succeeded",
                createdAt = "2026-08-26T00:00:00Z"
            )
        )
        `when`(paymentApi.getPayments())
            .thenReturn(Response.success(mockPayments))

        val result = paymentRepository.getPayments()

        assertTrue(result.isSuccess)
        assertEquals(1, result.getOrNull()?.size)
    }
}

private fun <T> any(): T = org.mockito.Mockito.any<T>()
