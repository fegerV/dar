package com.daragent.data.repository

import com.daragent.core.network.api.ChatApi
import com.daragent.core.network.model.chat.ChatMessageRequest
import com.daragent.core.network.model.chat.ProjectCreateRequest
import com.daragent.domain.model.Generation
import com.daragent.domain.repository.ChatMessage
import com.daragent.domain.repository.ChatProject
import com.daragent.domain.repository.ChatRepository
import com.daragent.domain.repository.GenerationRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class ChatRepositoryImpl(
    private val chatApi: ChatApi,
) : ChatRepository {

    override suspend fun sendMessage(text: String, projectId: String?): Result<ChatMessage> =
        withContext(Dispatchers.IO) {
            runCatching {
                val response = chatApi.sendMessage(ChatMessageRequest(text, projectId))
                if (response.isSuccessful) {
                    response.body()!!.toDomain()
                } else {
                    throw Exception("Failed to send message: ${response.code()}")
                }
            }
        }

    override suspend fun createProject(recipientName: String?, occasion: String?, mood: String?): Result<ChatProject> =
        withContext(Dispatchers.IO) {
            runCatching {
                val response = chatApi.createProject(
                    ProjectCreateRequest(
                        recipientName = recipientName,
                        occasion = occasion,
                        mood = mood,
                    )
                )
                if (response.isSuccessful) {
                    response.body()!!.toDomain()
                } else {
                    throw Exception("Failed to create project: ${response.code()}")
                }
            }
        }

    override suspend fun getProject(projectId: String): Result<ChatProject> =
        withContext(Dispatchers.IO) {
            runCatching {
                val response = chatApi.getProject(projectId)
                if (response.isSuccessful) {
                    response.body()!!.toDomain()
                } else {
                    throw Exception("Failed to get project: ${response.code()}")
                }
            }
        }

    private fun com.daragent.core.network.model.chat.ChatMessageResponse.toDomain() = ChatMessage(
        id = id,
        projectId = projectId,
        text = text,
        sender = sender,
        suggestions = suggestions,
        createdAt = createdAt
    )

    private fun com.daragent.core.network.model.chat.ProjectResponse.toDomain() = ChatProject(
        id = id,
        status = status,
        recipientName = recipientName,
        occasion = occasion,
        mood = mood,
        createdAt = createdAt
    )
}

class GenerationRepositoryImpl(
    private val generationApi: com.daragent.core.network.GenerationApi,
) : GenerationRepository {

    override suspend fun createGeneration(projectId: String, templateVersionId: String?): Result<Generation> =
        withContext(Dispatchers.IO) {
            runCatching {
                val response = generationApi.createGeneration(
                    // NOTE: core/network's GenerationApi posts to /api/v1/generations, but the
                    // backend only exposes POST /api/v1/generations/projects/{project_id}
                    // (backend/app/api/v1/generations.py::start_generation) and expects
                    // GenerationStartRequest(force_regenerate, variables). The request DTO here
                    // (type, brief_id, photo_url) therefore does not match the server contract.
                    // Aligning this is part of the pending network-stack consolidation; it does
                    // not affect compilation. See data/network/api/ApiModule.kt::GenerationsApi
                    // for the legacy, server-correct variant.
                    com.daragent.core.network.model.CreateGenerationRequest(
                        // Placeholder mapping: this DTO (type, brief_id, photo_url) does not model
                        // the backend's GenerationStartRequest(force_regenerate, variables). "video_lite"
                        // matches the default type GenerationViewModel starts with.
                        type = "video_lite",
                        briefId = templateVersionId,
                        photoUrl = null,
                    )
                )
                if (response.isSuccessful) {
                    response.body()!!.toDomain()
                } else {
                    throw Exception("Failed to create generation: ${response.code()}")
                }
            }
        }

    override suspend fun getGeneration(generationId: String): Result<Generation> =
        withContext(Dispatchers.IO) {
            runCatching {
                val response = generationApi.getGeneration(generationId)
                if (response.isSuccessful) {
                    response.body()!!.toDomain()
                } else {
                    throw Exception("Failed to get generation: ${response.code()}")
                }
            }
        }

    override suspend fun listGenerations(): Result<List<Generation>> =
        withContext(Dispatchers.IO) {
            runCatching {
                val response = generationApi.getGenerations(null)
                if (response.isSuccessful) {
                    response.body().orEmpty().map { it.toDomain() }
                } else {
                    throw Exception("Failed to list generations: ${response.code()}")
                }
            }
        }

    private fun com.daragent.core.network.model.GenerationDto.toDomain() = Generation(
        id = id,
        projectId = projectId ?: "",
        status = status,
        progress = progress,
        currentStep = currentStep,
        estimatedSeconds = estimatedSeconds,
        // backend GenerationResponse exposes video_url; output_url is the legacy field name
        // and is kept as a fallback.
        outputUrl = videoUrl ?: outputUrl,
        errorMessage = errorMessage
    )
}
