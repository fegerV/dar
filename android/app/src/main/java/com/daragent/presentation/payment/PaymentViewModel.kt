package com.daragent.presentation.payment

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.daragent.domain.model.Entitlement
import com.daragent.domain.model.Payment
import com.daragent.domain.model.Wallet
import com.daragent.domain.repository.PaymentRepository
import com.daragent.di.ServiceLocator
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class PaymentState(
    val projectId: String = "",
    val amount: Double = 0.0,
    val wallet: Wallet? = null,
    val entitlements: List<Entitlement> = emptyList(),
    val selectedMethod: String = "card",
    val payment: Payment? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)

class PaymentViewModel(
    private val paymentRepository: PaymentRepository? = null
) : ViewModel() {
    private val repo = paymentRepository ?: ServiceLocator.paymentRepository
    private val _state = MutableStateFlow(PaymentState())
    val state: StateFlow<PaymentState> = _state

    fun init(projectId: String, amount: Double) {
        _state.value = _state.value.copy(projectId = projectId, amount = amount)
        loadWallet()
        loadEntitlements()
    }

    fun selectMethod(method: String) {
        _state.value = _state.value.copy(selectedMethod = method)
    }

    fun pay() {
        val projectId = _state.value.projectId
        val method = _state.value.selectedMethod
        _state.value = _state.value.copy(isLoading = true, error = null)
        viewModelScope.launch {
            val result = repo.createPayment(projectId, method)
            result.onSuccess { payment ->
                _state.value = _state.value.copy(payment = payment, isLoading = false)
            }.onFailure { e ->
                _state.value = _state.value.copy(error = e.message, isLoading = false)
            }
        }
    }

    fun useEntitlement(entitlementId: String) {
        _state.value = _state.value.copy(isLoading = true, error = null)
        viewModelScope.launch {
            val result = repo.consumeEntitlement(entitlementId)
            result.onSuccess { entitlement ->
                _state.value = _state.value.copy(
                    entitlements = _state.value.entitlements.map { if (it.id == entitlement.id) entitlement else it },
                    isLoading = false
                )
            }.onFailure { e ->
                _state.value = _state.value.copy(error = e.message, isLoading = false)
            }
        }
    }

    private fun loadWallet() {
        viewModelScope.launch {
            repo.wallet().onSuccess { wallet ->
                _state.value = _state.value.copy(wallet = wallet)
            }
        }
    }

    private fun loadEntitlements() {
        viewModelScope.launch {
            repo.listEntitlements().onSuccess { entitlements ->
                _state.value = _state.value.copy(entitlements = entitlements)
            }
        }
    }
}
