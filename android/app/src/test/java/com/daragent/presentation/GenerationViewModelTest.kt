package com.daragent.presentation

import com.daragent.core.network.GenerationApi
import com.daragent.core.network.model.CreateGenerationRequest
import com.daragent.core.network.model.GenerationDto
import com.daragent.data.generation.GenerationRepository
import com.daragent.presentation.generation.GenerationStatus
import com.daragent.presentation.generation.GenerationViewModel
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.TestCoroutineScheduler
import kotlinx.coroutines.test.advanceTimeBy
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import okhttp3.ResponseBody.Companion.toResponseBody
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import retrofit2.Response

/**
 * Drives GenerationViewModel on a StandardTestDispatcher so polling (delay(2000) x60) advances
 * on virtual time. runCurrent() is used where only the start call should execute, and
 * advanceUntilIdle() where the poll loop must run to a terminal state.
 *
 * The repository is the real [GenerationRepository] backed by a fake [GenerationApi] rather
 * than a Mockito mock. Mockito reports stubs for Kotlin suspend functions as "Unused" (the
 * hidden Continuation parameter breaks invocation matching), then returns its null default;
 * because kotlin.Result is a value class that null unboxes to Result.success(null), the
 * ViewModel saw `generation = null` and threw inside `.id`. A fake API keeps the real
 * repository logic under test and makes the responses fully deterministic.
 */
@OptIn(ExperimentalCoroutinesApi::class)
class GenerationViewModelTest {

    private val scheduler = TestCoroutineScheduler()
    private val testDispatcher = StandardTestDispatcher(scheduler)
    private lateinit var api: FakeGenerationApi
    private lateinit var viewModel: GenerationViewModel

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        api = FakeGenerationApi()
        viewModel = GenerationViewModel(GenerationRepository(api))
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
        viewModel.startGeneration()
        runCurrent()

        assertEquals(GenerationStatus.PROCESSING, viewModel.uiState.value.status)
    }

    @Test
    fun `startGeneration failure should set FAILED status`() = runTest(scheduler) {
        api.createResponse = { Response.error(500, "boom".toResponseBody(null)) }

        viewModel.startGeneration()
        advanceUntilIdle()

        assertEquals(GenerationStatus.FAILED, viewModel.uiState.value.status)
        assertNotNull(viewModel.uiState.value.errorMessage)
    }

    @Test
    fun `completed generation should set COMPLETED with output url`() = runTest(scheduler) {
        api.pollResponse = { Response.success(dto("completed", outputUrl = "https://video.url")) }

        viewModel.startGeneration()
        advanceUntilIdle()

        assertEquals(GenerationStatus.COMPLETED, viewModel.uiState.value.status)
        assertEquals(100, viewModel.uiState.value.progress)
        assertEquals("https://video.url", viewModel.uiState.value.outputUrl)
    }

    @Test
    fun `failed generation should surface the server error`() = runTest(scheduler) {
        api.pollResponse = { Response.success(dto("failed", errorMessage = "boom")) }

        viewModel.startGeneration()
        advanceUntilIdle()

        assertEquals(GenerationStatus.FAILED, viewModel.uiState.value.status)
        assertEquals("boom", viewModel.uiState.value.errorMessage)
    }

    @Test
    fun `cancelGeneration should set CANCELLED status`() = runTest(scheduler) {
        viewModel.startGeneration()
        runCurrent()
        viewModel.cancelGeneration()

        assertEquals(GenerationStatus.CANCELLED, viewModel.uiState.value.status)
    }

    @Test
    fun `reset should return to IDLE state`() = runTest(scheduler) {
        viewModel.startGeneration()
        runCurrent()
        viewModel.reset()

        assertEquals(GenerationStatus.IDLE, viewModel.uiState.value.status)
        assertEquals(0, viewModel.uiState.value.progress)
        assertNull(viewModel.uiState.value.outputUrl)
    }

    @Test
    fun `progress should increase while processing`() = runTest(scheduler) {
        viewModel.startGeneration()
        advanceTimeBy(10_000)

        assertEquals(GenerationStatus.PROCESSING, viewModel.uiState.value.status)
        assertTrue(viewModel.uiState.value.progress > 0)
    }
}

private fun dto(
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

private class FakeGenerationApi : GenerationApi {
    /** Response returned by createGeneration; defaults to a freshly accepted job. */
    var createResponse: () -> Response<GenerationDto> = { Response.success(dto("processing")) }

    /** Response returned by every getGeneration poll. */
    var pollResponse: () -> Response<GenerationDto> = { Response.success(dto("processing")) }

    override suspend fun createGeneration(request: CreateGenerationRequest): Response<GenerationDto> =
        createResponse()

    override suspend fun getGeneration(id: String): Response<GenerationDto> = pollResponse()

    override suspend fun getGenerations(status: String?): Response<List<GenerationDto>> =
        Response.success(emptyList())
}
