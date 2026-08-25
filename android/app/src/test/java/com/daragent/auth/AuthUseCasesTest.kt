package com.daragent.auth

import com.daragent.data.auth.AuthRepository
import com.daragent.domain.auth.IsLoggedInUseCase
import com.daragent.domain.auth.LogoutUseCase
import kotlinx.coroutines.test.runTest
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mock
import org.mockito.Mockito.*
import org.mockito.junit.MockitoJUnitRunner

@RunWith(MockitoJUnitRunner::class)
class AuthUseCasesTest {

    @Mock
    private lateinit var authRepository: AuthRepository
    private lateinit var isLoggedInUseCase: IsLoggedInUseCase
    private lateinit var logoutUseCase: LogoutUseCase

    @Before
    fun setup() {
        isLoggedInUseCase = IsLoggedInUseCase(authRepository)
        logoutUseCase = LogoutUseCase(authRepository)
    }

    @Test
    fun `IsLoggedInUseCase should return true when logged in`() = runTest {
        `when`(authRepository.isLoggedIn()).thenReturn(true)

        val result = isLoggedInUseCase()

        assertTrue(result)
    }

    @Test
    fun `IsLoggedInUseCase should return false when not logged in`() = runTest {
        `when`(authRepository.isLoggedIn()).thenReturn(false)

        val result = isLoggedInUseCase()

        assertFalse(result)
    }

    @Test
    fun `LogoutUseCase should call clearAuth on repository`() = runTest {
        logoutUseCase()

        verify(authRepository).clearAuth()
    }
}
