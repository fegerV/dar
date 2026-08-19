package com.daragent.presentation.feedback

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.daragent.domain.model.ReactionStats
import com.daragent.domain.repository.FeedbackRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class FeedbackUiState(
    val stats: ReactionStats? = null,
    val isLoading: Boolean = false,
    val error: String? = null,
    val submitSuccess: Boolean = false,
)

class FeedbackViewModel(
    private val feedbackRepository: FeedbackRepository,
) : ViewModel() {
    private val _state = MutableStateFlow(FeedbackUiState())
    val state: StateFlow<FeedbackUiState> = _state

    fun loadStats(projectId: String) {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true)
            feedbackRepository.getStats(projectId)
                .onSuccess { stats ->
                    _state.value = _state.value.copy(stats = stats, isLoading = false)
                }
                .onFailure { e ->
                    _state.value = _state.value.copy(error = e.message, isLoading = false)
                }
        }
    }

    fun addReaction(
        projectId: String,
        emoji: String,
        rating: Int? = null,
        comment: String? = null,
    ) {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true, submitSuccess = false)
            feedbackRepository.addReaction(projectId, emoji, rating, comment)
                .onSuccess {
                    _state.value = _state.value.copy(isLoading = false, submitSuccess = true)
                }
                .onFailure { e ->
                    _state.value = _state.value.copy(error = e.message, isLoading = false)
                }
        }
    }
}
