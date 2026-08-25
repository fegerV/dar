package com.daragent.auth

import com.daragent.core.security.TokenManager
import com.daragent.data.auth.AuthRepository
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mock
import org.mockito.Mockito.*
import org.mockito.junit.MockitoJUnitRunner

@RunWith(MockitoJUnitRunner::class)
class AuthRepositoryTest {

    @Mock
    private lateinit var tokenManager: TokenManager
    private lateinit var authRepository: AuthRepository

    @Before
    fun setup() {
        authRepository = AuthRepository(tokenManager)
    }

    @Test
    fun `isLoggedIn should return true when tokenManager has token`() = runTest {
        `when`(tokenManager.isLoggedIn()).thenReturn(true)

        val result = authRepository.isLoggedIn()

        assertTrue(result)
    }

    @Test
    fun `isLoggedIn should return false when tokenManager has no token`() = runTest {
        `when`(tokenManager.isLoggedIn()).thenReturn(false)

        val result = authRepository.isLoggedIn()

        assertFalse(result)
    }

    @Test
    fun `getAccessToken should return token from tokenManager`() = runTest {
        val expectedToken = "test_access_token"
        `when`(tokenManager.getAccessToken()).thenReturn(expectedToken)

        val result = authRepository.getAccessToken()

        assertEquals(expectedToken, result)
    }

    @Test
    fun `saveAuth should save tokens to tokenManager`() = runTest {
        val response = com.daragent.core.network.model.AuthResponse(
            accessToken = "new_access",
            refreshToken = "new_refresh",
            tokenType = "Bearer",
            user = mock()
        )

        authRepository.saveAuth(response)

        verify(tokenManager).saveTokens(
            response.accessToken,
            response.refreshToken
        )
    }

    @Test
    fun `clearAuth should clear tokens from tokenManager`() = runTest {
        authRepository.clearAuth()

        verify(tokenManager).clearTokens()
    }
}
