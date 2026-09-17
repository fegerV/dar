package com.daragent.domain.repository

interface FeedbackRepository {
    suspend fun addReaction(
        projectId: String,
        emoji: String,
        rating: Int?,
        comment: String?,
    ): Result<Unit>

    suspend fun getStats(projectId: String): Result<com.daragent.domain.model.ReactionStats>
}
