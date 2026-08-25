package com.daragent.domain.auth

import com.daragent.data.auth.AuthRepository
import com.daragent.core.network.model.AuthResponse
import javax.inject.Inject

class LoginUseCase @Inject constructor(
    private val authRepository: AuthRepository,
) {
    suspend operator fun invoke(email: String, password: String): Result<AuthResponse> {
        return runCatching {
            throw NotImplementedError("Requires API integration")
        }
    }
}

class RegisterUseCase @Inject constructor(
    private val authRepository: AuthRepository,
) {
    suspend operator fun invoke(email: String, password: String, name: String?): Result<AuthResponse> {
        return runCatching {
            throw NotImplementedError("Requires API integration")
        }
    }
}

class LogoutUseCase @Inject constructor(
    private val authRepository: AuthRepository,
) {
    operator fun invoke() {
        authRepository.clearAuth()
    }
}

class IsLoggedInUseCase @Inject constructor(
    private val authRepository: AuthRepository,
) {
    operator fun invoke(): Boolean = authRepository.isLoggedIn()
}
