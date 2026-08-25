package com.daragent.integration

import com.daragent.core.network.api.PaymentApi
import com.daragent.core.network.model.CreatePaymentRequest
import com.daragent.core.network.model.PaymentResponse
import kotlinx.coroutines.test.runTest
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class PaymentIntegrationTest {

    private lateinit var mockWebServer: MockWebServer
    private lateinit var paymentApi: PaymentApi

    @Before
    fun setup() {
        mockWebServer = MockWebServer()
        mockWebServer.start()

        val retrofit = Retrofit.Builder()
            .baseUrl(mockWebServer.url("/"))
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        paymentApi = retrofit.create(PaymentApi::class.java)
    }

    @After
    fun tearDown() {
        mockWebServer.shutdown()
    }

    @Test
    fun createPayment_success_returnsPaymentData() = runTest {
        val mockResponse = """
        {
            "payment_id": "pay_test_123",
            "confirmation_url": "https://yookassa.ru/pay/test_123"
        }
        """.trimIndent()

        mockWebServer.enqueue(
            MockResponse()
                .setResponseCode(201)
                .setBody(mockResponse)
        )

        val response = paymentApi.createPayment(
            CreatePaymentRequest(amount = 499.0, currency = "RUB")
        )

        assertEquals(201, response.code())
        assertEquals("pay_test_123", response.body()?.paymentId)
        assertNotNull(response.body()?.confirmationUrl)
    }

    @Test
    fun createPayment_invalidAmount_returns400() = runTest {
        mockWebServer.enqueue(
            MockResponse()
                .setResponseCode(400)
                .setBody("""{"detail": "Invalid amount"}""")
        )

        val response = paymentApi.createPayment(
            CreatePaymentRequest(amount = -100.0, currency = "RUB")
        )

        assertEquals(400, response.code())
    }

    @Test
    fun getPayment_success_returnsPaymentStatus() = runTest {
        val mockResponse = """
        {
            "id": "pay_test_123",
            "amount": 499.0,
            "status": "succeeded",
            "created_at": "2026-08-26T00:00:00Z"
        }
        """.trimIndent()

        mockWebServer.enqueue(
            MockResponse()
                .setResponseCode(200)
                .setBody(mockResponse)
        )

        val response = paymentApi.getPayment("pay_test_123")

        assertTrue(response.isSuccessful)
        assertEquals("succeeded", response.body()?.status)
        assertEquals(499.0, response.body()?.amount)
    }

    @Test
    fun getPayment_notFound_returns404() = runTest {
        mockWebServer.enqueue(
            MockResponse()
                .setResponseCode(404)
                .setBody("""{"detail": "Payment not found"}""")
        )

        val response = paymentApi.getPayment("non_existent")

        assertEquals(404, response.code())
    }

    @Test
    fun getPayments_success_returnsList() = runTest {
        val mockResponse = """
        [
            {
                "id": "pay_1",
                "amount": 499.0,
                "status": "succeeded",
                "created_at": "2026-08-26T00:00:00Z"
            },
            {
                "id": "pay_2",
                "amount": 999.0,
                "status": "pending",
                "created_at": "2026-08-25T00:00:00Z"
            }
        ]
        """.trimIndent()

        mockWebServer.enqueue(
            MockResponse()
                .setResponseCode(200)
                .setBody(mockResponse)
        )

        val response = paymentApi.getPayments()

        assertTrue(response.isSuccessful)
        assertEquals(2, response.body()?.size)
    }
}
