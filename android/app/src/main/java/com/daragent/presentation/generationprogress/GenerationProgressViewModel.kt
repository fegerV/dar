package com.daragent.presentation.generationprogress

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.daragent.data.network.stream.SseClient
import com.daragent.domain.model.Generation
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class GenerationProgressState(
    val generation: Generation? = null,
    val steps: List<GenerationStep> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

data class GenerationStep(
    val stepNo: Int,
    val stepCode: String,
    val type: String,
    val status: String,
    val startedAt: String?,
    val completedAt: String?
)

class GenerationProgressViewModel(
    private val accessToken: String,
    private val baseUrl: String = "https://api.daragent.ru/api/v1"
) : ViewModel() {
    private val _state = MutableStateFlow(GenerationProgressState())
    val state: StateFlow<GenerationProgressState> = _state

    fun startStreaming(generationId: String) {
        _state.value = GenerationProgressState(isLoading = true)
        viewModelScope.launch {
            SseClient.streamGenerationProgress(
                baseUrl = baseUrl,
                generationId = generationId,
                accessToken = accessToken,
                onEvent = { event ->
                    val current = _state.value
                    val generation = Generation(
                        id = event.generationId,
                        projectId = current.generation?.projectId ?: "",
                        status = event.status,
                        progress = event.progress,
                        currentStep = event.currentStep,
                        estimatedSeconds = event.estimatedSeconds
                    )
                    _state.value = current.copy(
                        generation = generation,
                        isLoading = false,
                        error = null
                    )
                },
                onError = { error ->
                    _state.value = _state.value.copy(
                        isLoading = false,
                        error = error.message ?: "Ошибка подключения"
                    )
                },
                onComplete = {
                    _state.value = _state.value.copy(isLoading = false)
                }
            )
        }
    }
}
