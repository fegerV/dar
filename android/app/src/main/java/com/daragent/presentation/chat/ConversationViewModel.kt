package com.daragent.presentation.chat

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.daragent.core.network.model.PersonDto
import com.daragent.presentation.chat.model.ConversationState
import com.daragent.presentation.chat.model.Message
import com.daragent.presentation.chat.model.SuggestionAction
import com.daragent.domain.conversation.GetPeopleUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class ConversationUiState(
    val messages: List<Message> = emptyList(),
    val isLoading: Boolean = false,
    val currentState: ConversationState = ConversationState.IDLE,
    val inputText: String = "",
    val isRecording: Boolean = false,
    val people: List<PersonDto> = emptyList(),
    val error: String? = null,
)

@HiltViewModel
class ConversationViewModel @Inject constructor(
    private val getPeopleUseCase: GetPeopleUseCase,
) : ViewModel() {

    private val _uiState = MutableStateFlow(ConversationUiState())
    val uiState: StateFlow<ConversationUiState> = _uiState.asStateFlow()

    init {
        addWelcomeMessage()
        loadPeople()
    }

    private fun addWelcomeMessage() {
        val welcome = Message.Welcome(userName = null)
        val chips = Message.QuickChips(
            chips = listOf("Маму", "Папу", "Друга", "Коллегу", "Вторую половинку"),
        )
        _uiState.update {
            it.copy(messages = listOf(welcome, chips))
        }
    }

    private fun loadPeople() {
        viewModelScope.launch {
            getPeopleUseCase().fold(
                onSuccess = { people ->
                    _uiState.update {
                        it.copy(
                            people = people,
                            chips = createChipsFromPeople(people),
                        )
                    }
                },
                onFailure = { error ->
                    _uiState.update {
                        it.copy(error = error.message)
                    }
                }
            )
        }
    }

    private fun createChipsFromPeople(people: List<PersonDto>): List<String> {
        if (people.isEmpty()) {
            return listOf("Маму", "Папу", "Друга", "Коллегу", "Вторую половинку")
        }
        return people.take(5).map { it.name }
    }

    fun onChipSelected(chip: String) {
        sendMessage(chip)
    }

    fun onInputTextChanged(text: String) {
        _uiState.update { it.copy(inputText = text) }
    }

    fun onSendMessage() {
        val text = _uiState.value.inputText.trim()
        if (text.isNotEmpty()) {
            sendMessage(text)
            _uiState.update { it.copy(inputText = "") }
        }
    }

    private fun sendMessage(text: String) {
        val userMessage = Message.Text(text = text, isFromUser = true)
        _uiState.update {
            it.copy(
                messages = it.messages + userMessage,
                isLoading = true,
                currentState = ConversationState.AWAITING_INPUT,
                error = null,
            )
        }
        processUserMessage(text)
    }

    private fun processUserMessage(text: String) {
        viewModelScope.launch {
            kotlinx.coroutines.delay(500)

            val response = generateResponse(text)

            _uiState.update {
                it.copy(
                    messages = it.messages + response,
                    isLoading = false,
                    currentState = ConversationState.IDLE,
                )
            }
        }
    }

    private fun generateResponse(userText: String): Message {
        val lowerText = userText.lowercase()
        return when {
            lowerText.contains("мам") || lowerText.contains("маму") -> {
                Message.SuggestionCard(
                    title = "Мама ❤️",
                    subtitle = "Расскажи мне о ней поближе",
                    actions = listOf(
                        SuggestionAction("День рождения") {},
                        SuggestionAction("Юбилей") {},
                        SuggestionAction("Просто так") {},
                    ),
                )
            }
            lowerText.contains("пап") || lowerText.contains("папу") -> {
                Message.SuggestionCard(
                    title = "Папа 💙",
                    subtitle = "Какой у него праздник?",
                    actions = listOf(
                        SuggestionAction("День рождения") {},
                        SuggestionAction("Юбилей") {},
                    ),
                )
            }
            lowerText.contains("друг") -> {
                Message.SuggestionCard(
                    title = "Друг 🤝",
                    subtitle = "Давай придумаем что-то классное!",
                    actions = listOf(
                        SuggestionAction("День рождения") {},
                        SuggestionAction("Выпускной") {},
                    ),
                )
            }
            lowerText.contains("фото") -> {
                Message.PhotoRequest(text = "Отлично! Загрузи фото 📸")
            }
            else -> {
                Message.Text(
                    text = "Интересно! Расскажи подробнее о человеке, которого хочешь поздравить 🦊",
                    isFromUser = false,
                )
            }
        }
    }

    fun onPhotoRequested() {
        val photoRequest = Message.PhotoRequest(text = "Загрузи фото человека 📸")
        _uiState.update {
            it.copy(
                messages = it.messages + photoRequest,
                currentState = ConversationState.AWAITING_PHOTO,
            )
        }
    }

    fun onVoiceRecordingStart() {
        _uiState.update { it.copy(isRecording = true) }
    }

    fun onVoiceRecordingEnd(text: String?) {
        _uiState.update { it.copy(isRecording = false) }
        if (!text.isNullOrBlank()) {
            sendMessage(text)
        }
    }

    fun onSuggestionAction(action: SuggestionAction) {
        action.onClick()
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }

    fun clearMessages() {
        _uiState.update { ConversationUiState() }
        addWelcomeMessage()
    }
}
