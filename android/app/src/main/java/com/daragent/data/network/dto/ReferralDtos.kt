package com.daragent.data.network.dto

import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class ReferralCodeResponseDto(
    val id: String,
    val code: String,
    val uses_count: Int,
    val max_uses: Int?,
    val is_active: Boolean,
    val created_at: String,
)

@JsonClass(generateAdapter = true)
data class ReferralResponseDto(
    val id: String,
    val referrer_user_id: String,
    val referred_user_id: String?,
    val code: String,
    val status: String,
    val referrer_bonus_granted: Boolean,
    val referee_bonus_granted: Boolean,
    val completed_at: String?,
    val created_at: String,
)

@JsonClass(generateAdapter = true)
data class ReferralStatsResponseDto(
    val referral_code: String?,
    val total_referrals: Int,
    val completed_referrals: Int,
    val referrer_bonus_granted: Int,
    val referee_bonus_granted: Int,
    val earned_rub: Double,
    val referrer_bonus_rub: Double,
    val referee_bonus_rub: Double,
)

@JsonClass(generateAdapter = true)
data class ContactImportRequestDto(
    val contacts: List<Map<String, Any?>>,
    val consent_given: Boolean,
)

@JsonClass(generateAdapter = true)
data class ContactImportResponseDto(
    val imported: Int,
    val skipped: Int,
)

@JsonClass(generateAdapter = true)
data class ReactionRequestDto(
    val emoji: String,
    val rating: Int? = null,
    val comment: String? = null,
    val negative_details: Map<String, Any?>? = null,
)

@JsonClass(generateAdapter = true)
data class ReactionResponseDto(
    val id: String,
    val project_id: String,
    val emoji: String,
    val rating: Int?,
    val comment: String?,
    val created_at: String,
)

@JsonClass(generateAdapter = true)
data class ReactionStatsResponseDto(
    val project_id: String,
    val total_reactions: Int,
    val by_emoji: Map<String, Int>,
    val average_rating: Double?,
    val negative_count: Int,
)
