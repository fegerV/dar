package com.daragent.domain.chat

import com.daragent.core.network.model.chat.ChatMessageResponse
import com.daragent.core.network.model.chat.ProjectResponse
import com.daragent.data.chat.ChatRepository
import javax.inject.Inject

class SendMessageUseCase @Inject constructor(
    private val chatRepository: ChatRepository,
) {
    suspend operator fun invoke(text: String, projectId: String? = null): Result<ChatMessageResponse> {
        return chatRepository.sendMessage(text, projectId)
    }
}

class CreateProjectUseCase @Inject constructor(
    private val chatRepository: ChatRepository,
) {
    suspend operator fun invoke(
        recipientName: String?,
        recipientId: String?,
        occasion: String?,
        mood: String?,
    ): Result<ProjectResponse> {
        return chatRepository.createProject(
            recipientName = recipientName,
            recipientId = recipientId,
            occasion = occasion,
            mood = mood,
        )
    }
}

class GetProjectUseCase @Inject constructor(
    private val chatRepository: ChatRepository,
) {
    suspend operator fun invoke(projectId: String): Result<ProjectResponse> {
        return chatRepository.getProject(projectId)
    }
}
