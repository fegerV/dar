package com.daragent.domain.model

data class Reaction(
    val id: String,
    val projectId: String,
    val emoji: String,
    val rating: Int?,
    val comment: String?,
    val createdAt: String,
)

data class ReactionStats(
    val projectId: String,
    val totalReactions: Int,
    val byEmoji: Map<String, Int>,
    val averageRating: Double?,
    val negativeCount: Int,
)
