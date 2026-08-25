package com.daragent.data.auth

import com.daragent.core.network.TokenManager
import com.daragent.core.network.model.*
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val tokenManager: TokenManager,
) {

    fun isLoggedIn(): Boolean = tokenManager.isLoggedIn()

    fun getAccessToken(): String? = tokenManager.getAccessToken()

    fun saveAuth(response: AuthResponse) {
        tokenManager.saveTokens(response.accessToken, response.refreshToken)
    }

    fun clearAuth() {
        tokenManager.clearTokens()
    }
}
