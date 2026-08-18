package com.daragent.presentation.payment

import android.content.Context
import android.content.Intent
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.daragent.domain.model.Entitlement
import com.daragent.domain.model.Payment
import com.daragent.domain.model.Wallet
import com.daragent.domain.repository.PaymentRepository
import com.daragent.di.ServiceLocator
import kotlinx.coroutines.delay
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
    val checkoutUrl: String? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)

class PaymentViewModel(
    private val paymentRepository: PaymentRepository? = null,
    private val context: Context? = null
) : ViewModel() {
    private val repo = paymentRepository ?: ServiceLocator.paymentRepository
    private val cache = ServiceLocator.localCacheRepository
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
                _state.value = _state.value.copy(payment = payment, checkoutUrl = payment.confirmationUrl, isLoading = false)
                cachePaymentLocally(payment)
                if (payment.status == "pending" && !payment.confirmationUrl.isNullOrBlank()) {
                    launchCheckout(payment.confirmationUrl)
                }
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

    private fun launchCheckout(url: String) {
        val appContext = context ?: return
        val intent = Intent(appContext, com.daragent.YooKassaCheckoutActivity::class.java).apply {
            putExtra("checkout_url", url)
            putExtra("return_url", "daragent://yookassa/return")
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        appContext.startActivity(intent)
    }

    fun pollPaymentStatus() {
        val paymentId = _state.value.payment?.id ?: return
        viewModelScope.launch {
            while (true) {
                val result = repo.getPayment(paymentId)
                result.onSuccess { payment ->
                    _state.value = _state.value.copy(payment = payment)
                    if (payment.status in setOf("paid", "failed", "canceled")) {
                        cachePaymentLocally(payment)
                        break
                    }
                }.onFailure {
                    // ignore polling errors
                }
                delay(3000)
            }
        }
    }

    private fun loadWallet() {
        viewModelScope.launch {
            repo.wallet().onSuccess { wallet ->
                _state.value = _state.value.copy(wallet = wallet)
                cache.cacheWallet(com.daragent.data.local.entity.WalletEntity(wallet.userId, wallet.balanceRub, wallet.bonusBalance, wallet.updatedAt))
            }
        }
    }

    private fun loadEntitlements() {
        viewModelScope.launch {
            repo.listEntitlements().onSuccess { entitlements ->
                _state.value = _state.value.copy(entitlements = entitlements)
                entitlements.forEach { cache.cacheEntitlement(com.daragent.data.local.entity.EntitlementEntity(it.id, it.userId, it.code, it.quantity, it.consumed, it.expiresAt, it.source, it.createdAt)) }
            }
        }
    }

    private suspend fun cachePaymentLocally(payment: com.daragent.domain.model.Payment) {
        cache.cachePayment(com.daragent.data.local.entity.PaymentEntity(payment.id, payment.userId, payment.projectId, payment.amount, payment.status, payment.method, null, null, payment.createdAt, null))
    }
}
