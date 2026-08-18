package com.daragent.data.network.dto

import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class ProjectCreateRequest(
    val recipient_id: String,
    val occasion_code: String,
    val occasion_title: String? = null,
    val title: String? = null
)

@JsonClass(generateAdapter = true)
data class ProjectResponseDto(
    val id: String,
    val owner_user_id: String,
    val recipient_id: String?,
    val title: String?,
    val status: String,
    val visibility: String,
    val occasion_code: String?,
    val occasion_title: String?,
    val selected_recommendation_id: String?,
    val selected_template_version_id: String?,
    val final_generation_id: String?,
    val price_rub: Double,
    val bonus_discount_rub: Double,
    val promo_discount_rub: Double,
    val paid_rub: Double,
    val created_at: String,
    val updated_at: String,
    val completed_at: String?,
    val cancelled_at: String?
)

@JsonClass(generateAdapter = true)
data class ProjectListResponse(
    val items: List<ProjectResponseDto> = emptyList(),
    val total: Int = 0,
    val page: Int = 1,
    val page_size: Int = 20
)

@JsonClass(generateAdapter = true)
data class BriefUpdateRequest(
    val occasion_text: String? = null,
    val sender_role: String? = null,
    val recipient_role: String? = null,
    val relationship: String? = null,
    val relationship_text: String? = null,
    val desired_mood: String? = null,
    val desired_length_sec: Int? = null,
    val humor_level: Int? = null,
    val emotion_level: Int? = null,
    val surprise_level: Int? = null,
    val personalization_level: Int? = null,
    val inside_joke: String? = null,
    val hobbies_text: String? = null,
    val character_traits: String? = null,
    val memorable_story: String? = null,
    val desired_phrase: String? = null,
    val forbidden_topics: String? = null,
    val sender_message: String? = null,
    val personalization_answers: Map<String, Any>? = null,
    val selected_options: Map<String, Any>? = null
)

@JsonClass(generateAdapter = true)
data class BriefResponseDto(
    val id: String,
    val project_id: String,
    val status: String,
    val occasion_text: String?,
    val sender_role: String?,
    val recipient_role: String?,
    val relationship: String?,
    val relationship_text: String?,
    val desired_mood: String?,
    val desired_length_sec: Int?,
    val humor_level: Int?,
    val emotion_level: Int?,
    val surprise_level: Int?,
    val personalization_level: Int?,
    val inside_joke: String?,
    val hobbies_text: String?,
    val character_traits: String?,
    val memorable_story: String?,
    val desired_phrase: String?,
    val forbidden_topics: String?,
    val sender_message: String?,
    val personalization_answers: Map<String, Any>? = null,
    val selected_options: Map<String, Any>? = null,
    val created_at: String,
    val updated_at: String,
    val completed_at: String?
)

@JsonClass(generateAdapter = true)
data class RecommendationResponseDto(
    val id: String,
    val project_id: String,
    val template_version_id: String,
    val status: String,
    val rank: Int,
    val score: Float?,
    val match_reasons: List<String>,
    val explanation: String?,
    val generated_by_model: String?,
    val created_at: String,
    val selected_at: String?
)

@JsonClass(generateAdapter = true)
data class RecommendationListResponse(
    val items: List<RecommendationResponseDto> = emptyList()
)

@JsonClass(generateAdapter = true)
data class RecommendationSelectResponse(
    val id: String,
    val project_id: String,
    val selected_template_version_id: String,
    val status: String
)
