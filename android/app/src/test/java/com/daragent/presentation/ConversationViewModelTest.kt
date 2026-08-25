package com.daragent.presentation

import app.cash.turbine.test
import com.daragent.core.network.model.chat.ChatMessageResponse
import com.daragent.domain.chat.SendMessageUseCase
import com.daragent.domain.conversation.GetPeopleUseCase
import com.daragent.presentation.chat.ConversationViewModel
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

@OptIn(ExperimentalCoroutinesApi::class)
@RunWith(MockitoJUnitRunner::class)
class ConversationViewModelTest {

    @Mock
    private lateinit var getPeopleUseCase: GetPeopleUseCase
    @Mock
    private lateinit var sendMessageUseCase: SendMessageUseCase

    private lateinit var viewModel: ConversationViewModel
    private val testDispatcher = UnconfinedTestDispatcher()

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
    fun `initial state should have welcome message`() = runTest {
        viewModel.uiState.test {
            val state = awaitItem()
            assertTrue(state.messages.isNotEmpty())
            assertTrue(state.messages.first() is com.daragent.presentation.chat.model.Message.Welcome)
            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `onChipSelected should add user message`() = runTest {
        `when`(sendMessageUseCase(any(), any()))
            .thenReturn(Result.success(mockResponse()))

        viewModel.onChipSelected("Маму")

        viewModel.uiState.test {
            val state = awaitItem()
            val userMessages = state.messages.filterIsInstance<com.daragent.presentation.chat.model.Message.Text>().filter { it.isFromUser }
            assertTrue(userMessages.any { it.text == "Маму" })
            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `onSendMessage should clear input text`() = runTest {
        `when`(sendMessageUseCase(any(), any()))
            .thenReturn(Result.success(mockResponse()))

        viewModel.onInputTextChanged("Привет")
        viewModel.onSendMessage()

        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals("", state.inputText)
            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `onSendMessage should not send empty message`() = runTest {
        viewModel.onInputTextChanged("")
        viewModel.onSendMessage()

        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals(1, state.messages.size)
            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `onVoiceRecordingEnd with text should send message`() = runTest {
        `when`(sendMessageUseCase(any(), any()))
            .thenReturn(Result.success(mockResponse()))

        viewModel.onVoiceRecordingEnd("Привет от голоса")

        viewModel.uiState.test {
            val state = awaitItem()
            val userMessages = state.messages.filterIsInstance<com.daragent.presentation.chat.model.Message.Text>().filter { it.isFromUser }
            assertTrue(userMessages.any { it.text == "Привет от голоса" })
            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `clearError should reset error state`() = runTest {
        viewModel.clearError()

        viewModel.uiState.test {
            val state = awaitItem()
            assertNull(state.error)
            cancelAndIgnoreRemainingEvents()
        }
    }

    private fun mockResponse() = ChatMessageResponse(
        id = "msg_123",
        projectId = "proj_123",
        text = "Ответ Дарагента",
        sender = "daragent",
        suggestions = listOf("Маму", "Папу"),
        createdAt = "2026-08-26T00:00:00Z"
    )

    private inline fun <reified T> any(): T = org.mockito.Mockito.any<T>()
}
