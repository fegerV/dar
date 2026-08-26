package com.daragent.data.auth

import com.daragent.core.network.AuthApi
import com.daragent.core.network.TokenManager
import com.daragent.core.network.model.*
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val authApi: AuthApi,
    private val tokenManager: TokenManager,
) {

    fun isLoggedIn(): Boolean = tokenManager.isLoggedIn()

    fun getAccessToken(): String? = tokenManager.getAccessToken()

    suspend fun login(email: String, password: String): Result<AuthResponse> {
        return runCatching {
            val response = authApi.login(LoginRequest(email, password))
            if (response.isSuccessful) {
                val authResponse = response.body() ?: throw Exception("Empty response body")
                tokenManager.saveTokens(authResponse.accessToken, authResponse.refreshToken)
                authResponse
            } else {
                throw Exception("Login failed: ${response.code()}")
            }
        }
    }

    suspend fun register(email: String, password: String, name: String?): Result<AuthResponse> {
        return runCatching {
            val response = authApi.register(RegisterRequest(email, password, name))
            if (response.isSuccessful) {
                val authResponse = response.body() ?: throw Exception("Empty response body")
                tokenManager.saveTokens(authResponse.accessToken, authResponse.refreshToken)
                authResponse
            } else {
                throw Exception("Registration failed: ${response.code()}")
            }
        }
    }

    fun saveAuth(response: AuthResponse) {
        tokenManager.saveTokens(response.accessToken, response.refreshToken)
    }

    fun clearAuth() {
        tokenManager.clearTokens()
    }
}
