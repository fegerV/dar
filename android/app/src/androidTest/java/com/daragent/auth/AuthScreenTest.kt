package com.daragent.auth

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import com.daragent.presentation.auth.AuthScreen
import org.junit.Rule
import org.junit.Test

class AuthScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun authScreen_displaysWelcomeMessage() {
        composeTestRule.setContent {
            AuthScreen(
                onNavigateToLogin = {},
                onNavigateToRegister = {},
                onNavigateToOnboarding = {},
            )
        }

        composeTestRule.onNodeWithText("Привет! Я Дарагент").assertIsDisplayed()
    }

    @Test
    fun authScreen_displaysYandexButton() {
        composeTestRule.setContent {
            AuthScreen(
                onNavigateToLogin = {},
                onNavigateToRegister = {},
                onNavigateToOnboarding = {},
            )
        }

        composeTestRule.onNodeWithText("Войти через Яндекс").assertIsDisplayed()
    }

    @Test
    fun authScreen_displaysVkButton() {
        composeTestRule.setContent {
            AuthScreen(
                onNavigateToLogin = {},
                onNavigateToRegister = {},
                onNavigateToOnboarding = {},
            )
        }

        composeTestRule.onNodeWithText("Войти через VK").assertIsDisplayed()
    }

    @Test
    fun authScreen_displaysLoginButton() {
        composeTestRule.setContent {
            AuthScreen(
                onNavigateToLogin = {},
                onNavigateToRegister = {},
                onNavigateToOnboarding = {},
            )
        }

        composeTestRule.onNodeWithText("Логин и пароль").assertIsDisplayed()
    }

    @Test
    fun authScreen_navigateToLogin_onClick() {
        var navigatedToLogin = false

        composeTestRule.setContent {
            AuthScreen(
                onNavigateToLogin = { navigatedToLogin = true },
                onNavigateToRegister = {},
                onNavigateToOnboarding = {},
            )
        }

        composeTestRule.onNodeWithText("Логин и пароль").performClick()

        assert(navigatedToLogin) { "Should navigate to login screen" }
    }

    @Test
    fun authScreen_navigateToRegister_onClick() {
        var navigatedToRegister = false

        composeTestRule.setContent {
            AuthScreen(
                onNavigateToLogin = {},
                onNavigateToRegister = { navigatedToRegister = true },
                onNavigateToOnboarding = {},
            )
        }

        composeTestRule.onNodeWithText("Регистрация").performClick()

        assert(navigatedToRegister) { "Should navigate to register screen" }
    }
}
