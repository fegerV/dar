package com.daragent.data.repository

import com.daragent.data.network.api.FeedbackApi
import com.daragent.data.network.dto.ReactionRequestDto
import com.daragent.data.network.dto.ReactionStatsResponseDto
import com.daragent.domain.model.ReactionStats
import com.daragent.domain.repository.FeedbackRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class FeedbackRepositoryImpl(
    private val api: FeedbackApi,
) : FeedbackRepository {
    override suspend fun addReaction(
        projectId: String,
        emoji: String,
        rating: Int?,
        comment: String?,
    ): Result<Unit> = withContext(Dispatchers.IO) {
        runCatching {
            val response = api.addReaction(projectId, ReactionRequestDto(
                emoji = emoji,
                rating = rating,
                comment = comment,
            ))
            if (!response.isSuccessful) {
                throw Exception("Failed to add reaction: ${response.code()}")
            }
        }
    }

    override suspend fun getStats(projectId: String): Result<ReactionStats> = withContext(Dispatchers.IO) {
        runCatching {
            val resp = api.getStats(projectId)
            resp.body()?.toDomain() ?: throw Exception("Empty response body")
        }
    }
}

fun ReactionStatsResponseDto.toDomain(): ReactionStats {
    return ReactionStats(
        projectId = project_id,
        totalReactions = total_reactions,
        byEmoji = by_emoji,
        averageRating = average_rating,
        negativeCount = negative_count,
    )
}
