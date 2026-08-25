package com.daragent.integration

import com.daragent.core.network.api.AuthApi
import com.daragent.core.network.model.*
import kotlinx.coroutines.test.runTest
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class AuthIntegrationTest {

    private lateinit var mockWebServer: MockWebServer
    private lateinit var authApi: AuthApi

    @Before
    fun setup() {
        mockWebServer = MockWebServer()
        mockWebServer.start()

        val retrofit = Retrofit.Builder()
            .baseUrl(mockWebServer.url("/"))
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        authApi = retrofit.create(AuthApi::class.java)
    }

    @After
    fun tearDown() {
        mockWebServer.shutdown()
    }

    @Test
    fun login_success_returnsTokens() = runTest {
        val mockResponse = """
        {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "token_type": "bearer",
            "expires_in": 3600,
            "user": {
                "id": "123",
                "status": "active",
                "email": "test@example.com",
                "display_name": "Test User",
                "locale": "ru-RU",
                "timezone": "Europe/Moscow",
                "currency": "RUB",
                "created_at": "2026-08-26T00:00:00Z"
            }
        }
        """.trimIndent()

        mockWebServer.enqueue(
            MockResponse()
                .setResponseCode(200)
                .setBody(mockResponse)
        )

        val response = authApi.login(LoginRequest("test@example.com", "password123"))

        assertTrue(response.isSuccessful)
        assertEquals("test_access_token", response.body()?.accessToken)
        assertEquals("test_refresh_token", response.body()?.refreshToken)
    }

    @Test
    fun login_invalidCredentials_returns401() = runTest {
        mockWebServer.enqueue(
            MockResponse()
                .setResponseCode(401)
                .setBody("""{"detail": "Invalid credentials"}""")
        )

        val response = authApi.login(LoginRequest("wrong@example.com", "wrong"))

        assertEquals(401, response.code())
    }

    @Test
    fun login_networkError_returnsFailure() = runTest {
        mockWebServer.shutdown()

        val response = authApi.login(LoginRequest("test@example.com", "password"))

        assertFalse(response.isSuccessful)
    }

    @Test
    fun register_success_returnsTokens() = runTest {
        val mockResponse = """
        {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "token_type": "bearer",
            "expires_in": 3600,
            "user": {
                "id": "456",
                "status": "active",
                "email": "new@example.com",
                "display_name": "New User",
                "locale": "ru-RU",
                "timezone": "Europe/Moscow",
                "currency": "RUB",
                "created_at": "2026-08-26T00:00:00Z"
            }
        }
        """.trimIndent()

        mockWebServer.enqueue(
            MockResponse()
                .setResponseCode(201)
                .setBody(mockResponse)
        )

        val response = authApi.register(
            RegisterRequest(
                email = "new@example.com",
                password = "password123",
                displayName = "New User"
            )
        )

        assertEquals(201, response.code())
        assertEquals("new_access_token", response.body()?.accessToken)
    }
}
