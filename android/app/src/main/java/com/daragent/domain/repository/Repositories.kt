package com.daragent.domain.repository

import com.daragent.domain.model.Generation
import com.daragent.domain.model.Payment
import com.daragent.domain.model.Person
import com.daragent.domain.model.Template

interface PeopleRepository {
    suspend fun list(): Result<List<Person>>
    suspend fun create(person: Person): Result<Person>
}

interface TemplateRepository {
    suspend fun list(): Result<List<Template>>
    suspend fun get(id: String): Result<Template>
}

interface AuthRepository {
    suspend fun login(email: String, password: String): Result<AuthTokens>
    suspend fun register(email: String, password: String, displayName: String?): Result<AuthTokens>
    suspend fun me(): Result<UserProfile>
    fun getAccessToken(): String?
    fun clearTokens()
}

interface ChatRepository {
    suspend fun sendMessage(text: String, projectId: String? = null): Result<ChatMessage>
    suspend fun createProject(recipientName: String?, occasion: String?, mood: String?): Result<ChatProject>
    suspend fun getProject(projectId: String): Result<ChatProject>
}

interface PaymentRepository {
    suspend fun createPayment(projectId: String, method: String = "yookassa"): Result<Payment>
    suspend fun getPaymentStatus(paymentId: String): Result<Payment>
    suspend fun listPayments(): Result<List<Payment>>
}

interface GenerationRepository {
    suspend fun createGeneration(projectId: String, templateVersionId: String? = null): Result<Generation>
    suspend fun getGeneration(generationId: String): Result<Generation>
    suspend fun listGenerations(): Result<List<Generation>>
}

data class ChatMessage(
    val id: String,
    val projectId: String,
    val text: String,
    val sender: String,
    val suggestions: List<String>,
    val createdAt: String
)

data class ChatProject(
    val id: String,
    val status: String,
    val recipientName: String?,
    val occasion: String?,
    val mood: String?,
    val createdAt: String
)
