package com.daragent.presentation.profile

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.daragent.di.ServiceLocator
import com.daragent.domain.model.Entitlement
import com.daragent.domain.model.Payment
import com.daragent.domain.model.UserProfile
import com.daragent.domain.model.Wallet
import com.daragent.domain.repository.AuthRepository
import com.daragent.domain.repository.PaymentRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class ProfileState(
    val user: UserProfile? = null,
    val wallet: Wallet? = null,
    val entitlements: List<Entitlement> = emptyList(),
    val payments: List<Payment> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

class ProfileViewModel(
    private val authRepository: AuthRepository = ServiceLocator.authRepository,
    private val paymentRepository: PaymentRepository = ServiceLocator.paymentRepository
) : ViewModel() {
    private val _state = MutableStateFlow(ProfileState())
    val state: StateFlow<ProfileState> = _state

    init {
        loadProfile()
    }

    fun loadProfile() {
        _state.value = _state.value.copy(isLoading = true, error = null)
        viewModelScope.launch {
            try {
                val userResult = authRepository.me()
                val walletResult = paymentRepository.wallet()
                val entitlementsResult = paymentRepository.listEntitlements()
                _state.value = _state.value.copy(
                    user = userResult.getOrNull(),
                    wallet = walletResult.getOrNull(),
                    entitlements = entitlementsResult.getOrNull().orEmpty(),
                    isLoading = false
                )
            } catch (e: Exception) {
                _state.value = _state.value.copy(error = e.message, isLoading = false)
            }
        }
    }

    fun logout() {
        authRepository.clearTokens()
    }
}
