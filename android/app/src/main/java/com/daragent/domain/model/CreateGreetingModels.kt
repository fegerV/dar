package com.daragent.domain.model

data class Project(
    val id: String,
    val recipientId: String?,
    val title: String?,
    val status: String,
    val occasionCode: String?,
    val occasionTitle: String?,
    val priceRub: Double,
    val selectedTemplateVersionId: String? = null,
    val finalGenerationId: String? = null
)

data class Brief(
    val id: String,
    val projectId: String,
    val status: String,
    val occasionText: String?,
    val senderRole: String?,
    val recipientRole: String?,
    val relationship: String?,
    val desiredMood: String?,
    val humorLevel: Int?,
    val emotionLevel: Int?,
    val surpriseLevel: Int?,
    val insideJoke: String?,
    val hobbiesText: String?,
    val characterTraits: String?,
    val memorableStory: String?,
    val desiredPhrase: String?,
    val forbiddenTopics: String?,
    val senderMessage: String?
)

data class Recommendation(
    val id: String,
    val projectId: String,
    val templateVersionId: String,
    val rank: Int,
    val score: Float?,
    val matchReasons: List<String>,
    val explanation: String?,
    val selectedAt: String? = null
)

data class Occasion(
    val code: String,
    val title: String,
    val kind: String,
    val month: Int? = null,
    val day: Int? = null
)
