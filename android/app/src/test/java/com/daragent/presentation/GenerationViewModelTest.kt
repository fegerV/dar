package com.daragent.presentation

import com.daragent.core.network.model.GenerationDto
import com.daragent.data.generation.GenerationRepository
import com.daragent.presentation.generation.GenerationStatus
import com.daragent.presentation.generation.GenerationViewModel
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
 * Drives GenerationViewModel on a StandardTestDispatcher so polling (delay(2000) x60) advances
 * on virtual time. runCurrent() is used where only the start call should execute, and
 * advanceUntilIdle() where the poll loop must run to a terminal state.
 */
@OptIn(ExperimentalCoroutinesApi::class)
@RunWith(MockitoJUnitRunner::class)
class GenerationViewModelTest {

    @Mock
    private lateinit var generationRepository: GenerationRepository

    private lateinit var viewModel: GenerationViewModel
    private val scheduler = TestCoroutineScheduler()
    private val testDispatcher = StandardTestDispatcher(scheduler)

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        viewModel = GenerationViewModel(generationRepository)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `initial state should be IDLE`() {
        assertEquals(GenerationStatus.IDLE, viewModel.uiState.value.status)
        assertEquals(0, viewModel.uiState.value.progress)
    }

    @Test
    fun `startGeneration should move to PROCESSING while polling`() = runTest(scheduler) {
        whenever(generationRepository.createGeneration(any(), any(), any()))
            .thenReturn(Result.success(generation("processing")))

        viewModel.startGeneration()
        runCurrent()

        assertEquals(GenerationStatus.PROCESSING, viewModel.uiState.value.status)
    }

    @Test
    fun `startGeneration failure should set FAILED status`() = runTest(scheduler) {
        whenever(generationRepository.createGeneration(any(), any(), any()))
            .thenReturn(Result.failure(RuntimeException("Network error")))

        viewModel.startGeneration()
        advanceUntilIdle()

        assertEquals(GenerationStatus.FAILED, viewModel.uiState.value.status)
        assertNotNull(viewModel.uiState.value.errorMessage)
    }

    @Test
    fun `completed generation should set COMPLETED with output url`() = runTest(scheduler) {
        whenever(generationRepository.createGeneration(any(), any(), any()))
            .thenReturn(Result.success(generation("processing")))
        whenever(generationRepository.getGeneration(any()))
            .thenReturn(Result.success(generation("completed", outputUrl = "https://video.url")))

        viewModel.startGeneration()
        advanceUntilIdle()

        assertEquals(GenerationStatus.COMPLETED, viewModel.uiState.value.status)
        assertEquals(100, viewModel.uiState.value.progress)
        assertEquals("https://video.url", viewModel.uiState.value.outputUrl)
    }

    @Test
    fun `failed generation should surface the server error`() = runTest(scheduler) {
        whenever(generationRepository.createGeneration(any(), any(), any()))
            .thenReturn(Result.success(generation("processing")))
        whenever(generationRepository.getGeneration(any()))
            .thenReturn(Result.success(generation("failed", errorMessage = "boom")))

        viewModel.startGeneration()
        advanceUntilIdle()

        assertEquals(GenerationStatus.FAILED, viewModel.uiState.value.status)
        assertEquals("boom", viewModel.uiState.value.errorMessage)
    }

    @Test
    fun `cancelGeneration should set CANCELLED status`() = runTest(scheduler) {
        whenever(generationRepository.createGeneration(any(), any(), any()))
            .thenReturn(Result.success(generation("processing")))

        viewModel.startGeneration()
        runCurrent()
        viewModel.cancelGeneration()

        assertEquals(GenerationStatus.CANCELLED, viewModel.uiState.value.status)
    }

    @Test
    fun `reset should return to IDLE state`() = runTest(scheduler) {
        whenever(generationRepository.createGeneration(any(), any(), any()))
            .thenReturn(Result.success(generation("processing")))

        viewModel.startGeneration()
        runCurrent()
        viewModel.reset()

        assertEquals(GenerationStatus.IDLE, viewModel.uiState.value.status)
        assertEquals(0, viewModel.uiState.value.progress)
        assertNull(viewModel.uiState.value.outputUrl)
    }

    @Test
    fun `progress should increase while processing`() = runTest(scheduler) {
        whenever(generationRepository.createGeneration(any(), any(), any()))
            .thenReturn(Result.success(generation("processing")))
        whenever(generationRepository.getGeneration(any()))
            .thenReturn(Result.success(generation("processing")))

        viewModel.startGeneration()
        advanceTimeBy(10_000)

        assertEquals(GenerationStatus.PROCESSING, viewModel.uiState.value.status)
        assertTrue(viewModel.uiState.value.progress > 0)
    }

    private fun generation(
        status: String,
        outputUrl: String? = null,
        errorMessage: String? = null,
    ) = GenerationDto(
        id = "gen_123",
        type = "video_lite",
        status = status,
        progress = if (status == "completed") 100 else 50,
        outputUrl = outputUrl,
        cost = null,
        errorMessage = errorMessage,
        createdAt = "2026-08-26T00:00:00Z",
    )
}
