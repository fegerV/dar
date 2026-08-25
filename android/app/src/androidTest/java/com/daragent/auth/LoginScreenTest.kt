package com.daragent.auth

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import com.daragent.presentation.auth.LoginScreen
import org.junit.Rule
import org.junit.Test

class LoginScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginScreen_displaysEmailField() {
        composeTestRule.setContent {
            LoginScreen(onBack = {}, onNavigateToRegister = {}, onLoginSuccess = {})
        }

        composeTestRule.onNodeWithText("Email").assertIsDisplayed()
    }

    @Test
    fun loginScreen_displaysPasswordField() {
        composeTestRule.setContent {
            LoginScreen(onBack = {}, onNavigateToRegister = {}, onLoginSuccess = {})
        }

        composeTestRule.onNodeWithText("Пароль").assertIsDisplayed()
    }

    @Test
    fun loginScreen_displaysLoginButton() {
        composeTestRule.setContent {
            LoginScreen(onBack = {}, onNavigateToRegister = {}, onLoginSuccess = {})
        }

        composeTestRule.onNodeWithText("Войти").assertIsDisplayed()
    }

    @Test
    fun loginScreen_buttonDisabledWhenFieldsEmpty() {
        composeTestRule.setContent {
            LoginScreen(onBack = {}, onNavigateToRegister = {}, onLoginSuccess = {})
        }

        composeTestRule.onNodeWithText("Войти").assertIsNotEnabled()
    }

    @Test
    fun loginScreen_buttonEnabledWhenFieldsFilled() {
        composeTestRule.setContent {
            LoginScreen(onBack = {}, onNavigateToRegister = {}, onLoginSuccess = {})
        }

        composeTestRule.onNodeWithText("Email").performTextInput("test@example.com")
        composeTestRule.onNodeWithText("Пароль").performTextInput("password123")

        composeTestRule.onNodeWithText("Войти").assertIsEnabled()
    }

    @Test
    fun loginScreen_navigateToRegister_onClick() {
        var navigated = false

        composeTestRule.setContent {
            LoginScreen(
                onBack = {},
                onNavigateToRegister = { navigated = true },
                onLoginSuccess = {},
            )
        }

        composeTestRule.onNodeWithText("Зарегистрироваться").performClick()

        assert(navigated) { "Should navigate to register screen" }
    }
}
