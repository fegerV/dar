package com.daragent.presentation.chat

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.daragent.domain.model.Person
import com.daragent.domain.repository.ChatMessage
import com.daragent.presentation.chat.model.ConversationState
import com.daragent.presentation.chat.model.Message
import com.daragent.presentation.chat.model.SuggestionAction
import com.daragent.domain.chat.SendMessageUseCase
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
    val people: List<Person> = emptyList(),
    val error: String? = null,
    val currentProjectId: String? = null,
)

@HiltViewModel
class ConversationViewModel @Inject constructor(
    private val getPeopleUseCase: GetPeopleUseCase,
    private val sendMessageUseCase: SendMessageUseCase,
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
                    if (people.isNotEmpty()) {
                        updateWelcomeWithPeople(people)
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

    private fun createChipsFromPeople(people: List<Person>): List<String> {
        if (people.isEmpty()) {
            return listOf("Маму", "Папу", "Друга", "Коллегу", "Вторую половинку")
        }
        return people.take(5).map { it.name }
    }

    private fun updateWelcomeWithPeople(people: List<PersonDto>) {
        val updatedMessages = _uiState.value.messages.toMutableList()
        if (updatedMessages.isNotEmpty() && updatedMessages[0] is Message.Welcome) {
            updatedMessages[0] = Message.Welcome(userName = null)
        }
        _uiState.update { it.copy(messages = updatedMessages) }
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
            sendMessageUseCase(text, _uiState.value.currentProjectId).fold(
                onSuccess = { response ->
                    _uiState.update {
                        it.copy(currentProjectId = response.projectId)
                    }

                    val agentMessages = parseResponseToMessages(response)
                    _uiState.update {
                        it.copy(
                            messages = it.messages + agentMessages,
                            isLoading = false,
                            currentState = ConversationState.IDLE,
                        )
                    }
                },
                onFailure = { error ->
                    val errorMessage = Message.ErrorMessage(
                        text = "Не удалось отправить сообщение: ${error.message}",
                        onRetry = { sendMessage(text) },
                    )
                    _uiState.update {
                        it.copy(
                            messages = it.messages + errorMessage,
                            isLoading = false,
                            currentState = ConversationState.ERROR,
                        )
                    }
                }
            )
        }
    }

    private fun parseResponseToMessages(response: ChatMessage): List<Message> {
        val messages = mutableListOf<Message>()

        messages.add(
            Message.Text(
                text = response.text,
                isFromUser = false,
            )
        )

        if (response.suggestions.isNotEmpty()) {
            messages.add(
                Message.QuickChips(
                    chips = response.suggestions,
                )
            )
        }

        return messages
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

    fun createProject(
        recipientName: String?,
        occasion: String?,
        mood: String?,
    ) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
        }
    }
}
