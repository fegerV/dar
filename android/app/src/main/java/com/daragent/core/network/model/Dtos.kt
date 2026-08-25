package com.daragent.core.network.model

import com.squareup.moshi.Json
import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class LoginRequest(
    @Json(name = "email") val email: String,
    @Json(name = "password") val password: String,
)

@JsonClass(generateAdapter = true)
data class RegisterRequest(
    @Json(name = "email") val email: String,
    @Json(name = "password") val password: String,
    @Json(name = "name") val name: String?,
)

@JsonClass(generateAdapter = true)
data class RefreshRequest(
    @Json(name = "refresh_token") val refreshToken: String,
)

@JsonClass(generateAdapter = true)
data class AuthResponse(
    @Json(name = "access_token") val accessToken: String,
    @Json(name = "refresh_token") val refreshToken: String,
    @Json(name = "token_type") val tokenType: String,
    @Json(name = "user") val user: UserDto,
)

@JsonClass(generateAdapter = true)
data class UserDto(
    @Json(name = "id") val id: String,
    @Json(name = "email") val email: String,
    @Json(name = "name") val name: String?,
    @Json(name = "is_active") val isActive: Boolean,
    @Json(name = "created_at") val createdAt: String,
)

@JsonClass(generateAdapter = true)
data class UpdateUserRequest(
    @Json(name = "name") val name: String?,
)

@JsonClass(generateAdapter = true)
data class PersonDto(
    @Json(name = "id") val id: String,
    @Json(name = "owner_user_id") val ownerUserId: String,
    @Json(name = "name") val name: String,
    @Json(name = "relationship") val relationship: String?,
    @Json(name = "birth_date") val birthDate: String?,
    @Json(name = "interests") val interests: List<String>?,
    @Json(name = "notes") val notes: String?,
    @Json(name = "photo_url") val photoUrl: String?,
    @Json(name = "created_at") val createdAt: String,
)

@JsonClass(generateAdapter = true)
data class CreatePersonRequest(
    @Json(name = "name") val name: String,
    @Json(name = "relationship") val relationship: String?,
    @Json(name = "birth_date") val birthDate: String?,
    @Json(name = "interests") val interests: List<String>?,
    @Json(name = "notes") val notes: String?,
)

@JsonClass(generateAdapter = true)
data class UpdatePersonRequest(
    @Json(name = "name") val name: String?,
    @Json(name = "relationship") val relationship: String?,
    @Json(name = "birth_date") val birthDate: String?,
    @Json(name = "interests") val interests: List<String>?,
    @Json(name = "notes") val notes: String?,
)

@JsonClass(generateAdapter = true)
data class MessageRequest(
    @Json(name = "recipient_id") val recipientId: String?,
    @Json(name = "text") val text: String,
    @Json(name = "type") val type: String = "text",
)

@JsonClass(generateAdapter = true)
data class MessageResponse(
    @Json(name = "id") val id: String,
    @Json(name = "text") val text: String,
    @Json(name = "type") val type: String,
    @Json(name = "suggestions") val suggestions: List<String>?,
    @Json(name = "created_at") val createdAt: String,
)

@JsonClass(generateAdapter = true)
data class BriefDto(
    @Json(name = "id") val id: String,
    @Json(name = "recipient_id") val recipientId: String?,
    @Json(name = "recipient_name") val recipientName: String,
    @Json(name = "occasion") val occasion: String,
    @Json(name = "mood") val mood: String?,
    @Json(name = "concept") val concept: String?,
    @Json(name = "text") val text: String?,
    @Json(name = "status") val status: String,
    @Json(name = "created_at") val createdAt: String,
)

@JsonClass(generateAdapter = true)
data class CreateBriefRequest(
    @Json(name = "recipient_id") val recipientId: String?,
    @Json(name = "recipient_name") val recipientName: String,
    @Json(name = "occasion") val occasion: String,
    @Json(name = "mood") val mood: String?,
    @Json(name = "concept") val concept: String?,
    @Json(name = "text") val text: String?,
)

@JsonClass(generateAdapter = true)
data class UpdateBriefRequest(
    @Json(name = "recipient_name") val recipientName: String?,
    @Json(name = "occasion") val occasion: String?,
    @Json(name = "mood") val mood: String?,
    @Json(name = "concept") val concept: String?,
    @Json(name = "text") val text: String?,
)

@JsonClass(generateAdapter = true)
data class UploadResponse(
    @Json(name = "url") val url: String,
    @Json(name = "filename") val filename: String,
    @Json(name = "size") val size: Long,
)

@JsonClass(generateAdapter = true)
data class GenerationDto(
    @Json(name = "id") val id: String,
    @Json(name = "type") val type: String,
    @Json(name = "status") val status: String,
    @Json(name = "progress") val progress: Int?,
    @Json(name = "output_url") val outputUrl: String?,
    @Json(name = "cost") val cost: Double?,
    @Json(name = "error_message") val errorMessage: String?,
    @Json(name = "created_at") val createdAt: String,
)

@JsonClass(generateAdapter = true)
data class CreateGenerationRequest(
    @Json(name = "type") val type: String,
    @Json(name = "brief_id") val briefId: String?,
    @Json(name = "photo_url") val photoUrl: String?,
)

@JsonClass(generateAdapter = true)
data class PaymentDto(
    @Json(name = "id") val id: String,
    @Json(name = "amount") val amount: Double,
    @Json(name = "status") val status: String,
    @Json(name = "created_at") val createdAt: String,
)

@JsonClass(generateAdapter = true)
data class CreatePaymentRequest(
    @Json(name = "amount") val amount: Double,
    @Json(name = "currency") val currency: String = "RUB",
)

@JsonClass(generateAdapter = true)
data class PaymentResponse(
    @Json(name = "payment_id") val paymentId: String,
    @Json(name = "confirmation_url") val confirmationUrl: String?,
)

@JsonClass(generateAdapter = true)
data class WalletDto(
    @Json(name = "balance") val balance: Double,
    @Json(name = "currency") val currency: String,
)

@JsonClass(generateAdapter = true)
data class ReferralDto(
    @Json(name = "id") val id: String,
    @Json(name = "referred_user_name") val referredUserName: String?,
    @Json(name = "bonus_amount") val bonusAmount: Double,
    @Json(name = "created_at") val createdAt: String,
)

@JsonClass(generateAdapter = true)
data class ReferralCodeDto(
    @Json(name = "code") val code: String,
    @Json(name = "uses_count") val usesCount: Int,
)

@JsonClass(generateAdapter = true)
data class FeedbackRequest(
    @Json(name = "generation_id") val generationId: String,
    @Json(name = "rating") val rating: String,
    @Json(name = "comment") val comment: String?,
)
