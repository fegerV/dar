package com.daragent.core.network

import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class TokenManager @Inject constructor() {
    private var accessToken: String? = null
    private var refreshToken: String? = null

    fun getAccessToken(): String? = accessToken

    fun getRefreshToken(): String? = refreshToken

    fun saveTokens(access: String, refresh: String) {
        accessToken = access
        refreshToken = refresh
    }

    fun clearTokens() {
        accessToken = null
        refreshToken = null
    }

    fun isLoggedIn(): Boolean = accessToken != null
}
