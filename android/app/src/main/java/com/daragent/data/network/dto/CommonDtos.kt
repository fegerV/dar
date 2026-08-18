package com.daragent.data.network.dto

import com.squareup.moshi.Json
import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class RegisterRequest(
    val email: String,
    val password: String,
    val display_name: String? = null
)

@JsonClass(generateAdapter = true)
data class AuthResponse(
    val access_token: String,
    val refresh_token: String,
    val token_type: String,
    val expires_in: Long
)

@JsonClass(generateAdapter = true)
data class UserResponseDto(
    val id: String,
    val status: String,
    val display_name: String?,
    val first_name: String?,
    val last_name: String?,
    val email: String?,
    val phone: String?,
    val locale: String?,
    val timezone: String?,
    val currency: String?,
    val created_at: String
)

@JsonClass(generateAdapter = true)
data class LoginRequest(
    val email: String,
    val password: String
)

@JsonClass(generateAdapter = true)
data class PersonResponse(
    val id: String,
    val status: String,
    @Json(name = "first_name") val firstName: String?,
    @Json(name = "last_name") val lastName: String?,
    val nickname: String?,
    val gender: String?,
    @Json(name = "birth_date") val birthDate: String?,
    val city: String?,
    val occupation: String?,
    val relationship: String?,
    val notes: String?,
    val interests: List<String> = emptyList(),
    val traits: List<String> = emptyList(),
    val favorite_things: List<String> = emptyList(),
    val forbidden_topics: List<String> = emptyList(),
    val created_at: String,
    val updated_at: String
)

@JsonClass(generateAdapter = true)
data class RecipientListResponse(
    val items: List<PersonResponse> = emptyList(),
    val total: Int = 0,
    val page: Int = 1,
    val page_size: Int = 20
)

@JsonClass(generateAdapter = true)
data class CreatePersonRequest(
    @Json(name = "first_name") val firstName: String,
    @Json(name = "last_name") val lastName: String? = null,
    val nickname: String? = null,
    val gender: String? = null,
    @Json(name = "birth_date") val birthDate: String? = null,
    val city: String? = null,
    val occupation: String? = null,
    val relationship: String? = null,
    val notes: String? = null,
    val interests: List<String> = emptyList(),
    val traits: List<String> = emptyList(),
    val favorite_things: List<String> = emptyList(),
    val forbidden_topics: List<String> = emptyList()
)

@JsonClass(generateAdapter = true)
data class TemplateResponse(
    val id: String,
    val code: String,
    val title: String,
    val description: String?,
    val kind: String,
    val status: String,
    val category: String?,
    val occasion_codes: List<String>,
    val relationship_types: List<String>,
    val moods: List<String>,
    val base_price_rub: Double,
    val estimated_duration_sec: Int?,
    val personalization_score: Int?,
    val created_at: String
)

@JsonClass(generateAdapter = true)
data class TemplateListResponse(
    val items: List<TemplateResponse> = emptyList(),
    val total: Int = 0,
    val page: Int = 1,
    val page_size: Int = 20
)

@JsonClass(generateAdapter = true)
data class StartGenerationRequest(
    val force_regenerate: Boolean = false,
    val variables: Map<String, Any>? = null
)

@JsonClass(generateAdapter = true)
data class GenerationResponse(
    val id: String,
    val project_id: String,
    val status: String,
    val progress: Int,
    val current_step: String?,
    val estimated_seconds: Int?
)

@JsonClass(generateAdapter = true)
data class PaymentResponse(
    val id: String,
    val project_id: String?,
    val status: String,
    val method: String,
    val amount_rub: Double,
    val bonus_amount_rub: Double,
    val discount_rub: Double,
    val confirmation_url: String?,
    val created_at: String,
    val paid_at: String? = null
)

@JsonClass(generateAdapter = true)
data class WalletResponse(
    val user_id: String,
    val balance_rub: Double,
    val bonus_balance: Double,
    val updated_at: String
)

@JsonClass(generateAdapter = true)
data class EntitlementResponse(
    val id: String,
    val code: String,
    val quantity: Int,
    val consumed: Int,
    val expires_at: String?,
    val source: String?,
    val created_at: String
)

@JsonClass(generateAdapter = true)
data class ConsumeEntitlementRequest(
    val quantity: Int = 1
)

@JsonClass(generateAdapter = true)
data class HolidayResponseDto(
    val id: String,
    val code: String,
    val title: String,
    val kind: String,
    val month: Int?,
    val day: Int?,
    val country_code: String?,
    val description: String?,
    val status: String
)

@JsonClass(generateAdapter = true)
data class PaymentCreateRequest(
    val method: String,
    val return_url: String? = null,
    val promo_code: String? = null
)

@JsonClass(generateAdapter = true)
data class DeliveryResponseDto(
    val id: String,
    val project_id: String,
    val channel: String,
    val status: String,
    val destination: String?,
    val public_url: String?,
    val created_at: String,
    val scheduled_at: String?,
    val sent_at: String?,
    val opened_at: String?
)

@JsonClass(generateAdapter = true)
data class DeliveryListResponse(
    val items: List<DeliveryResponseDto> = emptyList()
)
