package com.daragent.presentation.payment

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.daragent.domain.payment.CreatePaymentUseCase
import com.daragent.domain.payment.GetPaymentStatusUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class PaymentUiState(
    val isLoading: Boolean = false,
    val isCompleted: Boolean = false,
    val error: String? = null,
    val confirmationUrl: String? = null,
    val paymentId: String? = null,
)

@HiltViewModel
class PaymentViewModel @Inject constructor(
    private val createPaymentUseCase: CreatePaymentUseCase,
    private val getPaymentStatusUseCase: GetPaymentStatusUseCase,
) : ViewModel() {

    private val _uiState = MutableStateFlow(PaymentUiState())
    val uiState: StateFlow<PaymentUiState> = _uiState.asStateFlow()

    fun createPayment() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }

            createPaymentUseCase(amount = 499.0, currency = "RUB").fold(
                onSuccess = { payment ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            paymentId = payment.id,
                            confirmationUrl = payment.confirmationUrl,
                        )
                    }
                },
                onFailure = { error ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            error = error.message ?: "Failed to create payment",
                        )
                    }
                }
            )
        }
    }

    fun verifyPayment() {
        val paymentId = _uiState.value.paymentId ?: return

        viewModelScope.launch {
            getPaymentStatusUseCase(paymentId).fold(
                onSuccess = { payment ->
                    if (payment.status == "succeeded") {
                        _uiState.update { it.copy(isCompleted = true) }
                    }
                },
                onFailure = { error ->
                    _uiState.update { it.copy(error = error.message) }
                }
            )
        }
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }

    fun reset() {
        _uiState.update { PaymentUiState() }
    }
}
