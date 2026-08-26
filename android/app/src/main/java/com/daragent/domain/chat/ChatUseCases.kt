package com.daragent.domain.chat

import com.daragent.domain.repository.ChatMessage
import com.daragent.domain.repository.ChatProject
import com.daragent.domain.repository.ChatRepository
import javax.inject.Inject

class SendMessageUseCase @Inject constructor(
    private val chatRepository: ChatRepository,
) {
    suspend operator fun invoke(text: String, projectId: String? = null): Result<ChatMessage> {
        return chatRepository.sendMessage(text, projectId)
    }
}

class CreateProjectUseCase @Inject constructor(
    private val chatRepository: ChatRepository,
) {
    suspend operator fun invoke(
        recipientName: String?,
        occasion: String?,
        mood: String?,
    ): Result<ChatProject> {
        return chatRepository.createProject(
            recipientName = recipientName,
            occasion = occasion,
            mood = mood,
        )
    }
}

class GetProjectUseCase @Inject constructor(
    private val chatRepository: ChatRepository,
) {
    suspend operator fun invoke(projectId: String): Result<ChatProject> {
        return chatRepository.getProject(projectId)
    }
}
