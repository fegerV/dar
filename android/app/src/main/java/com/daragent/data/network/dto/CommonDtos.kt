package com.daragent.data.network.dto

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
data class LoginRequest(
    val email: String,
    val password: String
)

@JsonClass(generateAdapter = true)
data class PersonResponse(
    val id: String,
    val name: String,
    val relationship: String,
    val birthDate: String?,
    val interests: List<String>,
    val insideJokes: List<String>
)

@JsonClass(generateAdapter = true)
data class CreatePersonRequest(
    val name: String,
    val relationship: String,
    val birthDate: String? = null,
    val interests: List<String> = emptyList(),
    val insideJokes: List<String> = emptyList()
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
data class StartGenerationRequest(
    val project_id: String,
    val template_version_id: String
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
data class CreatePaymentRequest(
    val project_id: String,
    val amount: Double
)

@JsonClass(generateAdapter = true)
data class PaymentResponse(
    val id: String,
    val user_id: String,
    val project_id: String?,
    val amount: Double,
    val status: String,
    val method: String,
    val created_at: String
)

@JsonClass(generateAdapter = true)
data class PaymentCreateRequest(
    val method: String
)

@JsonClass(generateAdapter = true)
data class WalletResponse(
    val user_id: String,
    val balance_rub: Double,
    val bonus_balance: Double
)

@JsonClass(generateAdapter = true)
data class EntitlementResponse(
    val id: String,
    val code: String,
    val quantity: Int,
    val consumed: Int,
    val expires_at: String?
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
