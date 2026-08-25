package com.daragent.presentation.chat.model

import java.util.UUID

sealed class Message {
    abstract val id: String
    abstract val timestamp: Long

    data class Text(
        override val id: String = UUID.randomUUID().toString(),
        override val timestamp: Long = System.currentTimeMillis(),
        val text: String,
        val isFromUser: Boolean = false,
    ) : Message()

    data class Welcome(
        override val id: String = UUID.randomUUID().toString(),
        override val timestamp: Long = System.currentTimeMillis(),
        val userName: String? = null,
    ) : Message()

    data class QuickChips(
        override val id: String = UUID.randomUUID().toString(),
        override val timestamp: Long = System.currentTimeMillis(),
        val chips: List<String>,
        val onChipClick: (String) -> Unit = {},
    ) : Message()

    data class SuggestionCard(
        override val id: String = UUID.randomUUID().toString(),
        override val timestamp: Long = System.currentTimeMillis(),
        val title: String,
        val subtitle: String? = null,
        val imageUrl: String? = null,
        val actions: List<SuggestionAction> = emptyList(),
    ) : Message()

    data class PhotoRequest(
        override val id: String = UUID.randomUUID().toString(),
        override val timestamp: Long = System.currentTimeMillis(),
        val text: String? = null,
    ) : Message()

    data class PhotoCard(
        override val id: String = UUID.randomUUID().toString(),
        override val timestamp: Long = System.currentTimeMillis(),
        val photoUrl: String,
        val caption: String? = null,
    ) : Message()

    data class VideoCard(
        override val id: String = UUID.randomUUID().toString(),
        override val timestamp: Long = System.currentTimeMillis(),
        val videoUrl: String,
        val thumbnailUrl: String? = null,
    ) : Message()

    data class GenerationProgress(
        override val id: String = UUID.randomUUID().toString(),
        override val timestamp: Long = System.currentTimeMillis(),
        val progress: Int = 0,
        val status: String = "generating",
        val message: String = "Создаём поздравление...",
    ) : Message()

    data class ErrorMessage(
        override val id: String = UUID.randomUUID().toString(),
        override val timestamp: Long = System.currentTimeMillis(),
        val text: String,
        val onRetry: (() -> Unit)? = null,
    ) : Message()

    data class ShareRequest(
        override val id: String = UUID.randomUUID().toString(),
        override val timestamp: Long = System.currentTimeMillis(),
        val videoUrl: String,
    ) : Message()
}

data class SuggestionAction(
    val label: String,
    val onClick: () -> Unit,
)

enum class ConversationState {
    IDLE,
    AWAITING_INPUT,
    AWAITING_PHOTO,
    GENERATING,
    ERROR,
}
