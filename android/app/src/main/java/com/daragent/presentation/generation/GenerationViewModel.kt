package com.daragent.presentation.generation

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.daragent.core.network.model.GenerationDto
import com.daragent.domain.generation.CreateGenerationUseCase
import com.daragent.domain.generation.GetGenerationUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

enum class GenerationStatus {
    IDLE,
    QUEUED,
    PROCESSING,
    COMPLETED,
    FAILED,
    CANCELLED,
}

data class GenerationUiState(
    val status: GenerationStatus = GenerationStatus.IDLE,
    val progress: Int = 0,
    val statusMessage: String = "Подготовка...",
    val outputUrl: String? = null,
    val errorMessage: String? = null,
    val generationId: String? = null,
)

@HiltViewModel
class GenerationViewModel @Inject constructor(
    private val createGenerationUseCase: CreateGenerationUseCase,
    private val getGenerationUseCase: GetGenerationUseCase,
) : ViewModel() {

    private val _uiState = MutableStateFlow(GenerationUiState())
    val uiState: StateFlow<GenerationUiState> = _uiState.asStateFlow()

    private var pollingJob: Job? = null

    fun startGeneration(
        type: String = "video_lite",
        briefId: String? = null,
        photoUrl: String? = null,
    ) {
        viewModelScope.launch {
            _uiState.update {
                it.copy(
                    status = GenerationStatus.QUEUED,
                    progress = 0,
                    statusMessage = "Создаём поздравление...",
                    errorMessage = null,
                )
            }

            createGenerationUseCase(
                type = type,
                briefId = briefId,
                photoUrl = photoUrl,
            ).fold(
                onSuccess = { generation ->
                    _uiState.update {
                        it.copy(
                            generationId = generation.id,
                            status = GenerationStatus.PROCESSING,
                            statusMessage = "Анализируем фото...",
                        )
                    }
                    startPolling(generation.id)
                },
                onFailure = { error ->
                    _uiState.update {
                        it.copy(
                            status = GenerationStatus.FAILED,
                            errorMessage = error.message ?: "Failed to start generation",
                        )
                    }
                }
            )
        }
    }

    private fun startPolling(generationId: String) {
        pollingJob?.cancel()
        pollingJob = viewModelScope.launch {
            var pollCount = 0
            val maxPolls = 60

            while (pollCount < maxPolls) {
                delay(2000)
                pollCount++

                getGenerationUseCase(generationId).fold(
                    onSuccess = { generation ->
                        when (generation.status) {
                            "completed" -> {
                                _uiState.update {
                                    it.copy(
                                        status = GenerationStatus.COMPLETED,
                                        progress = 100,
                                        statusMessage = "Готово!",
                                        outputUrl = generation.outputUrl,
                                    )
                                }
                                return@launch
                            }
                            "failed" -> {
                                _uiState.update {
                                    it.copy(
                                        status = GenerationStatus.FAILED,
                                        errorMessage = generation.errorMessage,
                                    )
                                }
                                return@launch
                            }
                            "cancelled" -> {
                                _uiState.update {
                                    it.copy(status = GenerationStatus.CANCELLED)
                                }
                                return@launch
                            }
                            else -> {
                                val progress = calculateProgress(pollCount)
                                val message = getStatusMessage(pollCount)
                                _uiState.update {
                                    it.copy(
                                        progress = progress,
                                        statusMessage = message,
                                    )
                                }
                            }
                        }
                    },
                    onFailure = { error ->
                        _uiState.update {
                            it.copy(
                                status = GenerationStatus.FAILED,
                                errorMessage = error.message,
                            )
                        }
                        return@launch
                    }
                )
            }

            _uiState.update {
                it.copy(
                    status = GenerationStatus.FAILED,
                    errorMessage = "Превышено время ожидания",
                )
            }
        }
    }

    private fun calculateProgress(pollCount: Int): Int {
        return when {
            pollCount <= 5 -> 10 + pollCount * 5
            pollCount <= 15 -> 35 + (pollCount - 5) * 3
            pollCount <= 30 -> 65 + (pollCount - 15) * 1
            else -> 80 + ((pollCount - 30) * 20 / 30).coerceAtMost(20)
        }.coerceIn(0, 99)
    }

    private fun getStatusMessage(pollCount: Int): String {
        return when {
            pollCount <= 3 -> "Анализируем фото..."
            pollCount <= 6 -> "Создаём сценарий..."
            pollCount <= 10 -> "Генерируем видео..."
            pollCount <= 20 -> "Добавляем эффекты..."
            pollCount <= 30 -> "Финальные штрихи..."
            else -> "Почти готово..."
        }
    }

    fun cancelGeneration() {
        pollingJob?.cancel()
        _uiState.update {
            it.copy(status = GenerationStatus.CANCELLED)
        }
    }

    fun reset() {
        pollingJob?.cancel()
        _uiState.update { GenerationUiState() }
    }

    override fun onCleared() {
        super.onCleared()
        pollingJob?.cancel()
    }
}
