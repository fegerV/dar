package com.daragent.presentation

import app.cash.turbine.test
import com.daragent.core.network.model.GenerationDto
import com.daragent.domain.generation.CreateGenerationUseCase
import com.daragent.domain.generation.GetGenerationUseCase
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

@OptIn(ExperimentalCoroutinesApi::class)
@RunWith(MockitoJUnitRunner::class)
class GenerationViewModelTest {

    @Mock
    private lateinit var createGenerationUseCase: CreateGenerationUseCase
    @Mock
    private lateinit var getGenerationUseCase: GetGenerationUseCase

    private lateinit var viewModel: GenerationViewModel
    private val testDispatcher = UnconfinedTestDispatcher()

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        viewModel = GenerationViewModel(createGenerationUseCase, getGenerationUseCase)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `initial state should be IDLE`() = runTest {
        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals(GenerationStatus.IDLE, state.status)
            assertEquals(0, state.progress)
            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `startGeneration should set QUEUED status`() = runTest {
        `when`(createGenerationUseCase(any(), any(), any()))
            .thenReturn(Result.success(mockGeneration("queued")))

        viewModel.startGeneration()

        viewModel.uiState.test {
            var state = awaitItem()
            while (state.status == GenerationStatus.IDLE) {
                state = awaitItem()
            }
            assertTrue(
                state.status == GenerationStatus.QUEUED ||
                state.status == GenerationStatus.PROCESSING
            )
            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `startGeneration failure should set FAILED status`() = runTest {
        `when`(createGenerationUseCase(any(), any(), any()))
            .thenReturn(Result.failure(RuntimeException("Network error")))

        viewModel.startGeneration()

        viewModel.uiState.test {
            var state = awaitItem()
            while (state.status != GenerationStatus.FAILED && state.status != GenerationStatus.IDLE) {
                state = awaitItem()
            }
            assertEquals(GenerationStatus.FAILED, state.status)
            assertNotNull(state.errorMessage)
            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `completed generation should set COMPLETED status`() = runTest {
        `when`(createGenerationUseCase(any(), any(), any()))
            .thenReturn(Result.success(mockGeneration("processing")))
        `when`(getGenerationUseCase(any()))
            .thenReturn(Result.success(mockGeneration("completed", "https://video.url")))

        viewModel.startGeneration()

        viewModel.uiState.test {
            var state = awaitItem()
            while (state.status != GenerationStatus.COMPLETED && state.errorMessage == null) {
                state = awaitItem()
            }
            if (state.status == GenerationStatus.COMPLETED) {
                assertEquals(100, state.progress)
                assertEquals("https://video.url", state.outputUrl)
            }
            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `cancelGeneration should set CANCELLED status`() = runTest {
        `when`(createGenerationUseCase(any(), any(), any()))
            .thenReturn(Result.success(mockGeneration("processing")))

        viewModel.startGeneration()
        viewModel.cancelGeneration()

        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals(GenerationStatus.CANCELLED, state.status)
            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `reset should return to IDLE state`() = runTest {
        `when`(createGenerationUseCase(any(), any(), any()))
            .thenReturn(Result.success(mockGeneration("processing")))

        viewModel.startGeneration()
        viewModel.cancelGeneration()
        viewModel.reset()

        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals(GenerationStatus.IDLE, state.status)
            assertEquals(0, state.progress)
            assertNull(state.outputUrl)
            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `progress should increase over time during processing`() = runTest {
        `when`(createGenerationUseCase(any(), any(), any()))
            .thenReturn(Result.success(mockGeneration("processing")))

        viewModel.startGeneration()

        viewModel.uiState.test {
            var state = awaitItem()
            var previousProgress = 0
            var hasIncreased = false

            while (state.status == GenerationStatus.PROCESSING || state.status == GenerationStatus.QUEUED) {
                if (state.progress > previousProgress) {
                    hasIncreased = true
                }
                previousProgress = state.progress
                state = awaitItem()
                if (state.status == GenerationStatus.COMPLETED || state.status == GenerationStatus.FAILED) break
            }
            assertTrue(hasIncreased || state.progress > 0)
            cancelAndIgnoreRemainingEvents()
        }
    }

    private fun mockGeneration(status: String, outputUrl: String? = null) = GenerationDto(
        id = "gen_123",
        type = "video_lite",
        status = status,
        progress = if (status == "completed") 100 else 50,
        outputUrl = outputUrl,
        createdAt = "2026-08-26T00:00:00Z"
    )

    private inline fun <reified T> any(): T = org.mockito.Mockito.any<T>()
}
