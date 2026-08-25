package com.daragent.core.network

import com.daragent.core.network.model.*
import retrofit2.Response
import retrofit2.http.*

interface AuthApi {
    @POST("/api/v1/auth/login")
    suspend fun login(@Body request: LoginRequest): Response<AuthResponse>

    @POST("/api/v1/auth/register")
    suspend fun register(@Body request: RegisterRequest): Response<AuthResponse>

    @POST("/api/v1/auth/refresh")
    suspend fun refresh(@Body request: RefreshRequest): Response<AuthResponse>
}

interface UserApi {
    @GET("/api/v1/users/me")
    suspend fun getCurrentUser(): Response<UserDto>

    @PATCH("/api/v1/users/me")
    suspend fun updateUser(@Body request: UpdateUserRequest): Response<UserDto>
}

interface PeopleApi {
    @GET("/api/v1/people")
    suspend fun getPeople(): Response<List<PersonDto>>

    @POST("/api/v1/people")
    suspend fun createPerson(@Body request: CreatePersonRequest): Response<PersonDto>

    @GET("/api/v1/people/{id}")
    suspend fun getPerson(@Path("id") id: String): Response<PersonDto>

    @PATCH("/api/v1/people/{id}")
    suspend fun updatePerson(
        @Path("id") id: String,
        @Body request: UpdatePersonRequest,
    ): Response<PersonDto>
}

interface ConversationApi {
    @POST("/api/v1/conversations/message")
    suspend fun sendMessage(@Body request: MessageRequest): Response<MessageResponse>
}

interface BriefApi {
    @POST("/api/v1/briefs")
    suspend fun createBrief(@Body request: CreateBriefRequest): Response<BriefDto>

    @GET("/api/v1/briefs/{id}")
    suspend fun getBrief(@Path("id") id: String): Response<BriefDto>

    @PATCH("/api/v1/briefs/{id}")
    suspend fun updateBrief(
        @Path("id") id: String,
        @Body request: UpdateBriefRequest,
    ): Response<BriefDto>
}

interface MediaApi {
    @Multipart
    @POST("/api/v1/media/upload")
    suspend fun uploadPhoto(@Part file: MultipartBody.Part): Response<UploadResponse>
}

interface GenerationApi {
    @POST("/api/v1/generations")
    suspend fun createGeneration(@Body request: CreateGenerationRequest): Response<GenerationDto>

    @GET("/api/v1/generations/{id}")
    suspend fun getGeneration(@Path("id") id: String): Response<GenerationDto>

    @GET("/api/v1/generations")
    suspend fun getGenerations(
        @Query("status") status: String?,
    ): Response<List<GenerationDto>>
}

interface PaymentApi {
    @POST("/api/v1/payments/create")
    suspend fun createPayment(@Body request: CreatePaymentRequest): Response<PaymentResponse>

    @GET("/api/v1/payments")
    suspend fun getPayments(): Response<List<PaymentDto>>

    @GET("/api/v1/payments/{id}")
    suspend fun getPayment(@Path("id") id: String): Response<PaymentDto>
}

interface WalletApi {
    @GET("/api/v1/wallet")
    suspend fun getWallet(): Response<WalletDto>
}

interface ReferralApi {
    @GET("/api/v1/referrals")
    suspend fun getReferrals(): Response<List<ReferralDto>>

    @GET("/api/v1/referrals/code")
    suspend fun getMyCode(): Response<ReferralCodeDto>
}

interface FeedbackApi {
    @POST("/api/v1/feedback")
    suspend fun submitFeedback(@Body request: FeedbackRequest): Response<Unit>
}
