package com.daragent.data.chat

import com.daragent.core.network.api.ChatApi
import com.daragent.core.network.model.chat.ChatMessageRequest
import com.daragent.core.network.model.chat.ChatMessageResponse
import com.daragent.core.network.model.chat.ProjectCreateRequest
import com.daragent.core.network.model.chat.ProjectResponse
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ChatRepository @Inject constructor(
    private val chatApi: ChatApi,
) {
    suspend fun sendMessage(text: String, projectId: String? = null): Result<ChatMessageResponse> {
        return runCatching {
            val request = ChatMessageRequest(text = text, projectId = projectId)
            val response = chatApi.sendMessage(request)
            if (response.isSuccessful) {
                response.body() ?: throw Exception("Empty response body")
            } else {
                throw Exception("Failed to send message: ${response.code()}")
            }
        }
    }

    suspend fun createProject(
        recipientName: String?,
        recipientId: String?,
        occasion: String?,
        mood: String?,
    ): Result<ProjectResponse> {
        return runCatching {
            val request = ProjectCreateRequest(
                recipientName = recipientName,
                recipientId = recipientId,
                occasion = occasion,
                mood = mood,
            )
            val response = chatApi.createProject(request)
            if (response.isSuccessful) {
                response.body() ?: throw Exception("Empty response body")
            } else {
                throw Exception("Failed to create project: ${response.code()}")
            }
        }
    }

    suspend fun getProject(projectId: String): Result<ProjectResponse> {
        return runCatching {
            val response = chatApi.getProject(projectId)
            if (response.isSuccessful) {
                response.body() ?: throw Exception("Empty response body")
            } else {
                throw Exception("Failed to get project: ${response.code()}")
            }
        }
    }
}
