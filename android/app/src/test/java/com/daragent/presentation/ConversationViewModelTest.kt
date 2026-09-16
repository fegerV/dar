package com.daragent.presentation

import com.daragent.domain.chat.SendMessageUseCase
import com.daragent.domain.conversation.GetPeopleUseCase
import com.daragent.domain.repository.ChatMessage
import com.daragent.presentation.chat.ConversationViewModel
import com.daragent.presentation.chat.model.Message
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mock
import org.mockito.junit.MockitoJUnitRunner
import org.mockito.kotlin.any
import org.mockito.kotlin.whenever

/**
 * Drives ConversationViewModel on a StandardTestDispatcher so the init-time loadPeople()
 * coroutine is queued (not run eagerly) and every stub is in place before the work executes.
 * State is read through uiState.value after advancing virtual time, which keeps the assertions
 * independent of coroutine scheduling.
 */
@OptIn(ExperimentalCoroutinesApi::class)
@RunWith(MockitoJUnitRunner::class)
class ConversationViewModelTest {

    @Mock
    private lateinit var getPeopleUseCase: GetPeopleUseCase
    @Mock
    private lateinit var sendMessageUseCase: SendMessageUseCase

    private lateinit var viewModel: ConversationViewModel
    private val scheduler = TestCoroutineScheduler()
    private val testDispatcher = StandardTestDispatcher(scheduler)

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        viewModel = ConversationViewModel(getPeopleUseCase, sendMessageUseCase)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `initial state should have welcome message`() = runTest(scheduler) {
        whenever(getPeopleUseCase()).thenReturn(Result.success(emptyList()))
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertTrue(state.messages.isNotEmpty())
        assertTrue(state.messages.first() is Message.Welcome)
    }

    @Test
    fun `onChipSelected should add user message`() = runTest(scheduler) {
        whenever(getPeopleUseCase()).thenReturn(Result.success(emptyList()))
        whenever(sendMessageUseCase(any(), any())).thenReturn(Result.success(agentReply()))

        viewModel.onChipSelected("Маму")
        advanceUntilIdle()

        val userMessages = viewModel.uiState.value.messages
            .filterIsInstance<Message.Text>()
            .filter { it.isFromUser }
        assertTrue(userMessages.any { it.text == "Маму" })
    }

    @Test
    fun `onSendMessage should clear input text`() = runTest(scheduler) {
        whenever(getPeopleUseCase()).thenReturn(Result.success(emptyList()))
        whenever(sendMessageUseCase(any(), any())).thenReturn(Result.success(agentReply()))

        viewModel.onInputTextChanged("Привет")
        viewModel.onSendMessage()
        advanceUntilIdle()

        assertEquals("", viewModel.uiState.value.inputText)
    }

    @Test
    fun `onSendMessage should not send empty message`() = runTest(scheduler) {
        whenever(getPeopleUseCase()).thenReturn(Result.success(emptyList()))
        advanceUntilIdle()

        val before = viewModel.uiState.value.messages.size

        viewModel.onInputTextChanged("   ")
        viewModel.onSendMessage()
        advanceUntilIdle()

        // Only the welcome + quick-chips messages added at init, nothing from the blank input.
        assertEquals(before, viewModel.uiState.value.messages.size)
    }

    @Test
    fun `onVoiceRecordingEnd with text should send message`() = runTest(scheduler) {
        whenever(getPeopleUseCase()).thenReturn(Result.success(emptyList()))
        whenever(sendMessageUseCase(any(), any())).thenReturn(Result.success(agentReply()))

        viewModel.onVoiceRecordingEnd("Привет от голоса")
        advanceUntilIdle()

        val userMessages = viewModel.uiState.value.messages
            .filterIsInstance<Message.Text>()
            .filter { it.isFromUser }
        assertTrue(userMessages.any { it.text == "Привет от голоса" })
    }

    @Test
    fun `onVoiceRecordingEnd with blank text should not send message`() = runTest(scheduler) {
        whenever(getPeopleUseCase()).thenReturn(Result.success(emptyList()))
        advanceUntilIdle()

        val before = viewModel.uiState.value.messages.size

        viewModel.onVoiceRecordingEnd("   ")
        advanceUntilIdle()

        assertEquals(before, viewModel.uiState.value.messages.size)
        assertFalse(viewModel.uiState.value.isRecording)
    }

    @Test
    fun `clearError should reset error state`() = runTest(scheduler) {
        whenever(getPeopleUseCase()).thenReturn(Result.success(emptyList()))
        advanceUntilIdle()

        viewModel.clearError()

        assertNull(viewModel.uiState.value.error)
    }

    private fun agentReply() = ChatMessage(
        id = "msg_123",
        projectId = "proj_123",
        text = "Ответ Дарагента",
        sender = "daragent",
        suggestions = listOf("Маму", "Папу"),
        createdAt = "2026-08-26T00:00:00Z",
    )
}
