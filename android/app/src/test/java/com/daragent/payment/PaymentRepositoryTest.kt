package com.daragent.payment

import com.daragent.core.network.PaymentApi
import com.daragent.core.network.model.CreatePaymentRequest
import com.daragent.core.network.model.PaymentDto
import com.daragent.core.network.model.PaymentResponse
import com.daragent.data.payment.PaymentRepository
import kotlinx.coroutines.test.runTest
import okhttp3.ResponseBody.Companion.toResponseBody
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import retrofit2.Response

/**
 * Uses the real [PaymentRepository] over a fake [PaymentApi] instead of a Mockito mock.
 *
 * Mockito cannot reliably stub Kotlin suspend functions: `when(mock.suspendFun(any()))`
 * fails with InvalidUseOfMatchersException / "any(...) must not be null", because the
 * recorded invocation carries a hidden Continuation parameter and the argument matchers
 * get out of step. Stubbing a plain fake removes that failure mode entirely.
 */
class PaymentRepositoryTest {

    private lateinit var api: FakePaymentApi
    private lateinit var paymentRepository: PaymentRepository

    @Before
    fun setup() {
        api = FakePaymentApi()
        paymentRepository = PaymentRepository(api)
    }

    @Test
    fun `createPayment should return success when API call succeeds`() = runTest {
        val result = paymentRepository.createPayment(499.0, "RUB")

        assertTrue(result.isSuccess)
        assertEquals("pay_123", result.getOrNull()?.id)
        assertEquals("https://yookassa.ru/pay/123", result.getOrNull()?.confirmationUrl)
    }

    @Test
    fun `createPayment should return failure when API call fails`() = runTest {
        api.createResponse = Response.error(500, "Error".toResponseBody(null))

        val result = paymentRepository.createPayment(499.0, "RUB")

        assertTrue(result.isFailure)
    }

    @Test
    fun `getPayment should return payment when API call succeeds`() = runTest {
        api.payment = PaymentDto(
            id = "pay_123",
            amount = 499.0,
            status = "succeeded",
            createdAt = "2026-08-26T00:00:00Z",
        )

        val result = paymentRepository.getPayment("pay_123")

        assertTrue(result.isSuccess)
        assertEquals("pay_123", result.getOrNull()?.id)
        assertEquals("succeeded", result.getOrNull()?.status)
    }

    @Test
    fun `getPayments should return list when API call succeeds`() = runTest {
        api.payments = listOf(
            PaymentDto(
                id = "pay_123",
                amount = 499.0,
                status = "succeeded",
                createdAt = "2026-08-26T00:00:00Z",
            )
        )

        val result = paymentRepository.getPayments()

        assertTrue(result.isSuccess)
        assertEquals(1, result.getOrNull()?.size)
    }
}

private class FakePaymentApi : PaymentApi {
    var createResponse: Response<PaymentResponse> =
        Response.success(
            PaymentResponse(
                paymentId = "pay_123",
                confirmationUrl = "https://yookassa.ru/pay/123",
            )
        )

    var payments: List<PaymentDto> = emptyList()
    var payment: PaymentDto? = null

    override suspend fun createPayment(request: CreatePaymentRequest): Response<PaymentResponse> =
        createResponse

    override suspend fun getPayments(): Response<List<PaymentDto>> = Response.success(payments)

    override suspend fun getPayment(id: String): Response<PaymentDto> =
        payment?.let { Response.success(it) }
            ?: Response.error(404, "not found".toResponseBody(null))
}
