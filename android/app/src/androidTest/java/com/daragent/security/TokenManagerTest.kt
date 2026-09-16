package com.daragent.security

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.daragent.core.security.TokenManager
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class TokenManagerTest {

    private lateinit var tokenManager: TokenManager
    private val context: Context = ApplicationProvider.getApplicationContext()

    @Before
    fun setup() {
        tokenManager = TokenManager(context)
        tokenManager.clearTokens()
    }

    @After
    fun tearDown() {
        tokenManager.clearTokens()
    }

    @Test
    fun `saveTokens should store access and refresh tokens`() = runTest {
        val accessToken = "test_access_token_12345"
        val refreshToken = "test_refresh_token_67890"

        tokenManager.saveTokens(accessToken, refreshToken)

        assertEquals(accessToken, tokenManager.getAccessToken())
        assertEquals(refreshToken, tokenManager.getRefreshToken())
    }

    @Test
    fun `clearTokens should remove all tokens`() = runTest {
        tokenManager.saveTokens("access", "refresh")
        tokenManager.clearTokens()

        assertNull(tokenManager.getAccessToken())
        assertNull(tokenManager.getRefreshToken())
        assertFalse(tokenManager.isLoggedIn())
    }

    @Test
    fun `isLoggedIn should return true when access token exists`() = runTest {
        tokenManager.saveTokens("access_token", "refresh_token")

        assertTrue(tokenManager.isLoggedIn())
    }

    @Test
    fun `isLoggedIn should return false when no tokens`() = runTest {
        assertFalse(tokenManager.isLoggedIn())
    }

    @Test
    fun `tokens should persist across instances`() = runTest {
        tokenManager.saveTokens("persistent_access", "persistent_refresh")

        val newInstance = TokenManager(context)

        assertEquals("persistent_access", newInstance.getAccessToken())
        assertEquals("persistent_refresh", newInstance.getRefreshToken())
    }
}
