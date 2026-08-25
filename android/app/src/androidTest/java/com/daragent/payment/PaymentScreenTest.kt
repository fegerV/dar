package com.daragent.payment

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import com.daragent.presentation.payment.PaymentScreen
import com.daragent.presentation.payment.PaymentViewModel
import org.junit.Rule
import org.junit.Test

class PaymentScreenTest {

    @get:Rule
    val composeTestRule = createAndroidComposeRule<TestActivity>()

    @Test
    fun paymentScreen_displaysAmount() {
        composeTestRule.setContent {
            PaymentScreen(onBack = {}, onPaymentComplete = {})
        }

        composeTestRule.onNodeWithText("499 ₽").assertIsDisplayed()
    }

    @Test
    fun paymentScreen_displaysPayButton() {
        composeTestRule.setContent {
            PaymentScreen(onBack = {}, onPaymentComplete = {})
        }

        composeTestRule.onNodeWithText("Оплатить 499 ₽").assertIsDisplayed()
    }

    @Test
    fun paymentScreen_payButtonClick_callsCreatePayment() {
        var paymentStarted = false

        composeTestRule.setContent {
            PaymentScreen(onBack = {}, onPaymentComplete = {})
        }

        composeTestRule.onNodeWithText("Оплатить 499 ₽").performClick()

        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule.onAllNodesWithText("Подготовка платежа...")
                .fetchSemanticsNodes().isNotEmpty()
        }
    }

    @Test
    fun paymentScreen_backButton_onClick() {
        var backClicked = false

        composeTestRule.setContent {
            PaymentScreen(onBack = { backClicked = true }, onPaymentComplete = {})
        }

        composeTestRule.onNodeWithContentDescription("Назад").performClick()

        assert(backClicked) { "Should call onBack" }
    }
}
