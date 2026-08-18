package com.daragent.domain.model

data class Person(
    val id: String,
    val name: String,
    val relationship: String,
    val birthDate: String?,
    val interests: List<String>,
    val insideJokes: List<String>
)

data class Template(
    val id: String,
    val title: String,
    val category: String,
    val previewUrl: String?,
    val priceRub: Double
)

data class Generation(
    val id: String,
    val projectId: String,
    val status: String,
    val progress: Int,
    val currentStep: String?,
    val estimatedSeconds: Int?
)

data class Wallet(
    val userId: String,
    val balanceRub: Double,
    val bonusBalance: Double,
    val updatedAt: String? = null
)

data class Entitlement(
    val id: String,
    val userId: String = "",
    val code: String,
    val quantity: Int,
    val consumed: Int,
    val expiresAt: String?,
    val source: String? = null,
    val createdAt: String = ""
)

data class Payment(
    val id: String,
    val userId: String = "",
    val projectId: String? = null,
    val amount: Double = 0.0,
    val status: String = "pending",
    val method: String = "",
    val confirmationUrl: String? = null,
    val createdAt: String = "",
    val paidAt: String? = null
)

data class AuthTokens(
    val accessToken: String,
    val refreshToken: String,
    val tokenType: String = "bearer",
    val expiresIn: Long = 0
)

data class UserProfile(
    val id: String,
    val email: String?,
    val displayName: String?,
    val phone: String? = null,
    val locale: String? = null,
    val createdAt: String
)
