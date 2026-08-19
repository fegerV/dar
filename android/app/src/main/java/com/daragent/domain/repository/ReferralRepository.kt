package com.daragent.domain.repository

import com.daragent.domain.model.Referral
import com.daragent.domain.model.ReferralCode
import com.daragent.domain.model.ReferralStats

interface ReferralRepository {
    suspend fun getMyCode(): Result<ReferralCode>
    suspend fun applyCode(code: String): Result<Referral>
    suspend fun getStats(): Result<ReferralStats>
}

interface FeedbackRepository {
    suspend fun addReaction(
        projectId: String,
        emoji: String,
        rating: Int?,
        comment: String?,
    ): Result<Unit>

    suspend fun getStats(projectId: String): Result<com.daragent.domain.model.ReactionStats>
}
