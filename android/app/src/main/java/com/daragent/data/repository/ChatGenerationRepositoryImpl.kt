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
                    ProjectCreateRequest(recipientName, occasion, mood)
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
        createdAt = created_at
    )

    private fun com.daragent.core.network.model.chat.ProjectResponse.toDomain() = ChatProject(
        id = id,
        status = status,
        recipientName = recipient_name,
        occasion = occasion,
        mood = mood,
        createdAt = created_at
    )
}

class GenerationRepositoryImpl(
    private val generationApi: com.daragent.core.network.GenerationApi,
) : GenerationRepository {

    override suspend fun createGeneration(projectId: String, templateVersionId: String?): Result<Generation> =
        withContext(Dispatchers.IO) {
            runCatching {
                val response = generationApi.createGeneration(
                    com.daragent.core.network.model.CreateGenerationRequest(projectId, templateVersionId)
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
        projectId = project_id,
        status = status,
        progress = progress,
        currentStep = current_step,
        estimatedSeconds = estimated_seconds
    )
}
