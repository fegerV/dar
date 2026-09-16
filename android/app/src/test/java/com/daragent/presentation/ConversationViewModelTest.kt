package com.daragent.presentation

import com.daragent.domain.chat.SendMessageUseCase
import com.daragent.domain.conversation.GetPeopleUseCase
import com.daragent.domain.model.Person
import com.daragent.domain.repository.ChatMessage
import com.daragent.domain.repository.ChatProject
import com.daragent.domain.repository.ChatRepository
import com.daragent.domain.repository.PeopleRepository
import com.daragent.presentation.chat.ConversationViewModel
import com.daragent.presentation.chat.model.Message
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.TestCoroutineScheduler
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test

/**
 * Drives ConversationViewModel on a StandardTestDispatcher so the init-time loadPeople()
 * coroutine is queued (not run eagerly) and every fake is already wired before the work runs.
 *
 * The collaborators are hand-written fakes rather than Mockito mocks. Mockito cannot
 * reliably stub Kotlin suspend functions: the recorded invocation carries the hidden
 * Continuation parameter, so a stub registered for `suspendFun()` is reported by Mockito
 * itself as "Unused" even though the call site executes, and the mock then falls back to
 * its null default. Because kotlin.Result is a value class, that null unboxes to
 * Result.success(null) -- not to a failure -- so the ViewModel received `people = null`
 * and died inside `ConversationUiState.copy`. Fakes remove the whole class of problem.
 */
@OptIn(ExperimentalCoroutinesApi::class)
class ConversationViewModelTest {

    private val peopleRepository = FakePeopleRepository()
    private val chatRepository = FakeChatRepository()
    private val scheduler = TestCoroutineScheduler()
    private val testDispatcher = StandardTestDispatcher(scheduler)
    private lateinit var viewModel: ConversationViewModel

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        viewModel = ConversationViewModel(
            GetPeopleUseCase(peopleRepository),
            SendMessageUseCase(chatRepository),
        )
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `initial state should have welcome message`() = runTest(scheduler) {
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertTrue(state.messages.isNotEmpty())
        assertTrue(state.messages.first() is Message.Welcome)
    }

    @Test
    fun `onChipSelected should add user message`() = runTest(scheduler) {
        viewModel.onChipSelected("Маму")
        advanceUntilIdle()

        val userMessages = viewModel.uiState.value.messages
            .filterIsInstance<Message.Text>()
            .filter { it.isFromUser }
        assertTrue(userMessages.any { it.text == "Маму" })
    }

    @Test
    fun `onSendMessage should clear input text`() = runTest(scheduler) {
        viewModel.onInputTextChanged("Привет")
        viewModel.onSendMessage()
        advanceUntilIdle()

        assertEquals("", viewModel.uiState.value.inputText)
    }

    @Test
    fun `onSendMessage should not send empty message`() = runTest(scheduler) {
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
        viewModel.onVoiceRecordingEnd("Привет от голоса")
        advanceUntilIdle()

        val userMessages = viewModel.uiState.value.messages
            .filterIsInstance<Message.Text>()
            .filter { it.isFromUser }
        assertTrue(userMessages.any { it.text == "Привет от голоса" })
    }

    @Test
    fun `onVoiceRecordingEnd with blank text should not send message`() = runTest(scheduler) {
        advanceUntilIdle()

        val before = viewModel.uiState.value.messages.size

        viewModel.onVoiceRecordingEnd("   ")
        advanceUntilIdle()

        assertEquals(before, viewModel.uiState.value.messages.size)
        assertFalse(viewModel.uiState.value.isRecording)
    }

    @Test
    fun `clearError should reset error state`() = runTest(scheduler) {
        peopleRepository.failure = RuntimeException("boom")
        // loadPeople() already ran against the empty fake during @Before, so rebuild the
        // ViewModel to exercise the failure branch, then clear it again.
        viewModel = ConversationViewModel(
            GetPeopleUseCase(peopleRepository),
            SendMessageUseCase(chatRepository),
        )
        advanceUntilIdle()
        assertEquals("boom", viewModel.uiState.value.error)

        viewModel.clearError()

        assertNull(viewModel.uiState.value.error)
    }
}

private class FakePeopleRepository : PeopleRepository {
    var people: List<Person> = emptyList()
    var failure: Throwable? = null

    override suspend fun list(): Result<List<Person>> =
        failure?.let { Result.failure(it) } ?: Result.success(people)

    override suspend fun create(person: Person): Result<Person> = Result.success(person)

    override suspend fun get(id: String): Result<Person> =
        Result.failure(NoSuchElementException(id))
}

private class FakeChatRepository : ChatRepository {
    override suspend fun sendMessage(text: String, projectId: String?): Result<ChatMessage> =
        Result.success(
            ChatMessage(
                id = "msg_123",
                projectId = projectId ?: "proj_123",
                text = "Ответ Дарагента",
                sender = "daragent",
                suggestions = listOf("Маму", "Папу"),
                createdAt = "2026-08-26T00:00:00Z",
            )
        )

    override suspend fun createProject(
        recipientName: String?,
        occasion: String?,
        mood: String?,
    ): Result<ChatProject> = Result.failure(UnsupportedOperationException("not used by this screen"))

    override suspend fun getProject(projectId: String): Result<ChatProject> =
        Result.failure(UnsupportedOperationException("not used by this screen"))
}
