package com.daragent.data.network.api

import com.daragent.data.network.NetworkModule
import com.daragent.data.network.dto.AuthResponse
import com.daragent.data.network.dto.BriefResponseDto
import com.daragent.data.network.dto.BriefUpdateRequest
import com.daragent.data.network.dto.ConsumeEntitlementRequest
import com.daragent.data.network.dto.CreatePersonRequest
import com.daragent.data.network.dto.DeliveryListResponse
import com.daragent.data.network.dto.EntitlementResponse
import com.daragent.data.network.dto.GenerationResponse
import com.daragent.data.network.dto.HolidayResponseDto
import com.daragent.data.network.dto.LoginRequest
import com.daragent.data.network.dto.PaymentCreateRequest
import com.daragent.data.network.dto.PaymentResponse
import com.daragent.data.network.dto.PersonResponse
import com.daragent.data.network.dto.ProjectCreateRequest
import com.daragent.data.network.dto.ProjectListResponse
import com.daragent.data.network.dto.ProjectResponseDto
import com.daragent.data.network.dto.RecommendationListResponse
import com.daragent.data.network.dto.RecommendationSelectResponse
import com.daragent.data.network.dto.RecipientListResponse
import com.daragent.data.network.dto.RegisterRequest
import com.daragent.data.network.dto.StartGenerationRequest
import com.daragent.data.network.dto.TemplateListResponse
import com.daragent.data.network.dto.TemplateResponse
import com.daragent.data.network.dto.WalletResponse
import com.daragent.data.network.dto.UserResponseDto
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path
import retrofit2.http.Query

interface AuthApi {
    @POST("auth/register")
    suspend fun register(@Body request: RegisterRequest): Response<AuthResponse>

    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<AuthResponse>

    @GET("auth/me")
    suspend fun me(): Response<UserResponseDto>
}

interface PeopleApi {
    @GET("recipients")
    suspend fun list(): Response<RecipientListResponse>

    @POST("recipients")
    suspend fun create(@Body request: CreatePersonRequest): Response<PersonResponse>
}

interface TemplatesApi {
    @GET("templates")
    suspend fun list(): Response<TemplateListResponse>

    @GET("templates/{id}")
    suspend fun get(@Path("id") id: String): Response<TemplateResponse>
}

interface ProjectsApi {
    @POST("projects")
    suspend fun create(@Body request: ProjectCreateRequest): Response<ProjectResponseDto>

    @GET("projects")
    suspend fun list(): Response<ProjectListResponse>
}

interface BriefsApi {
    @PUT("projects/{project_id}/brief")
    suspend fun update(@Path("project_id") projectId: String, @Body request: BriefUpdateRequest): Response<BriefResponseDto>

    @GET("projects/{project_id}/brief")
    suspend fun get(@Path("project_id") projectId: String): Response<BriefResponseDto>

    @POST("projects/{project_id}/brief/complete")
    suspend fun complete(@Path("project_id") projectId: String): Response<BriefResponseDto>
}

interface RecommendationsApi {
    @GET("recommendations/projects/{project_id}")
    suspend fun list(@Path("project_id") projectId: String): Response<RecommendationListResponse>

    @POST("recommendations/projects/{project_id}/select/{recommendation_id}")
    suspend fun select(
        @Path("project_id") projectId: String,
        @Path("recommendation_id") recommendationId: String
    ): Response<RecommendationSelectResponse>
}

interface GenerationsApi {
    @POST("generations/projects/{project_id}")
    suspend fun start(@Path("project_id") projectId: String, @Body request: StartGenerationRequest): Response<GenerationResponse>

    @GET("generations/{id}")
    suspend fun get(@Path("id") id: String): Response<GenerationResponse>
}

interface PaymentsApi {
    @POST("payments/projects/{project_id}")
    suspend fun create(@Path("project_id") projectId: String, @Body request: PaymentCreateRequest): Response<PaymentResponse>

    @GET("payments/{payment_id}")
    suspend fun get(@Path("payment_id") paymentId: String): Response<PaymentResponse>

    @GET("payments/wallet")
    suspend fun wallet(): Response<WalletResponse>

    @GET("payments/entitlements")
    suspend fun entitlements(): Response<List<EntitlementResponse>>

    @POST("payments/entitlements/{entitlement_id}/consume")
    suspend fun consumeEntitlement(@Path("entitlement_id") entitlementId: String, @Body request: ConsumeEntitlementRequest = ConsumeEntitlementRequest()): Response<EntitlementResponse>
}

interface HolidaysApi {
    @GET("holidays")
    suspend fun list(@Query("kind") kind: String? = null): Response<List<HolidayResponseDto>>
}

interface DeliveriesApi {
    @GET("delivery/projects/{project_id}")
    suspend fun byProject(@Path("project_id") projectId: String): Response<DeliveryListResponse>
}

object ApiModule {
    val authApi: AuthApi by lazy { NetworkModule.provideRetrofit().create(AuthApi::class.java) }
    val peopleApi: PeopleApi by lazy { NetworkModule.provideRetrofit().create(PeopleApi::class.java) }
    val templatesApi: TemplatesApi by lazy { NetworkModule.provideRetrofit().create(TemplatesApi::class.java) }
    val projectsApi: ProjectsApi by lazy { NetworkModule.provideRetrofit().create(ProjectsApi::class.java) }
    val briefsApi: BriefsApi by lazy { NetworkModule.provideRetrofit().create(BriefsApi::class.java) }
    val recommendationsApi: RecommendationsApi by lazy { NetworkModule.provideRetrofit().create(RecommendationsApi::class.java) }
    val generationsApi: GenerationsApi by lazy { NetworkModule.provideRetrofit().create(GenerationsApi::class.java) }
    val paymentsApi: PaymentsApi by lazy { NetworkModule.provideRetrofit().create(PaymentsApi::class.java) }
    val holidaysApi: HolidaysApi by lazy { NetworkModule.provideRetrofit().create(HolidaysApi::class.java) }
    val deliveriesApi: DeliveriesApi by lazy { NetworkModule.provideRetrofit().create(DeliveriesApi::class.java) }
}
