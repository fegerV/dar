package com.daragent.presentation.referral

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.daragent.domain.model.ReferralCode
import com.daragent.domain.model.ReferralStats
import com.daragent.domain.repository.ReferralRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class ReferralUiState(
    val code: ReferralCode? = null,
    val stats: ReferralStats? = null,
    val isLoading: Boolean = false,
    val error: String? = null,
)

class ReferralViewModel(
    private val referralRepository: ReferralRepository,
) : ViewModel() {
    private val _state = MutableStateFlow(ReferralUiState(isLoading = true))
    val state: StateFlow<ReferralUiState> = _state

    init {
        loadCode()
        loadStats()
    }

    fun loadCode() {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true)
            referralRepository.getMyCode()
                .onSuccess { code ->
                    _state.value = _state.value.copy(code = code, isLoading = false)
                }
                .onFailure { e ->
                    _state.value = _state.value.copy(error = e.message, isLoading = false)
                }
        }
    }

    fun loadStats() {
        viewModelScope.launch {
            referralRepository.getStats()
                .onSuccess { stats ->
                    _state.value = _state.value.copy(stats = stats)
                }
                .onFailure { e ->
                    _state.value = _state.value.copy(error = e.message)
                }
        }
    }

    fun applyCode(code: String) {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true)
            referralRepository.applyCode(code)
                .onSuccess {
                    _state.value = _state.value.copy(isLoading = false)
                }
                .onFailure { e ->
                    _state.value = _state.value.copy(error = e.message, isLoading = false)
                }
        }
    }
}
