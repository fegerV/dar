package com.daragent.data.repository

import com.daragent.data.local.AuthTokenManager
import com.daragent.data.network.api.AuthApi
import com.daragent.data.network.dto.AuthResponse
import com.daragent.domain.model.AuthTokens
import com.daragent.domain.model.UserProfile
import com.daragent.domain.repository.AuthRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class AuthRepositoryImpl(
    private val api: AuthApi,
    private val tokenManager: AuthTokenManager
) : AuthRepository {
    override suspend fun login(email: String, password: String): Result<AuthTokens> =
        withContext(Dispatchers.IO) {
            runCatching {
                val response = api.login(com.daragent.data.network.dto.LoginRequest(email, password)).body()!!
                val tokens = response.toDomain()
                tokenManager.saveTokens(tokens.accessToken, tokens.refreshToken)
                tokens
            }
        }

    override suspend fun register(email: String, password: String, displayName: String?): Result<AuthTokens> =
        withContext(Dispatchers.IO) {
            runCatching {
                val response = api.register(
                    com.daragent.data.network.dto.RegisterRequest(email, password, displayName)
                ).body()!!
                val tokens = response.toDomain()
                tokenManager.saveTokens(tokens.accessToken, tokens.refreshToken)
                tokens
            }
        }

    override suspend fun me(): Result<UserProfile> =
        withContext(Dispatchers.IO) {
            runCatching {
                api.me().body()!!.toDomain()
            }
        }

    override fun getAccessToken(): String? = tokenManager.getAccessToken()
    override fun clearTokens() = tokenManager.clearTokens()
}

private fun AuthResponse.toDomain() = AuthTokens(
    accessToken = access_token,
    refreshToken = refresh_token,
    tokenType = token_type,
    expiresIn = expires_in
)

private fun com.daragent.data.network.dto.UserResponseDto.toDomain() = UserProfile(
    id = id,
    email = email,
    displayName = display_name,
    phone = phone,
    locale = locale,
    createdAt = created_at
)
