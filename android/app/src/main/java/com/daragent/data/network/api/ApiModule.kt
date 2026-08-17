package com.daragent.data.network.api

import com.daragent.data.network.NetworkModule
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PATCH
import retrofit2.http.Path
import retrofit2.http.Query

interface AuthApi {
    @POST("auth/register")
    suspend fun register(@Body request: RegisterRequest): Response<AuthResponse>

    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<AuthResponse>
}

interface PeopleApi {
    @GET("people")
    suspend fun list(): Response<List<PersonResponse>>

    @POST("people")
    suspend fun create(@Body request: CreatePersonRequest): Response<PersonResponse>
}

interface TemplatesApi {
    @GET("templates")
    suspend fun list(): Response<List<TemplateResponse>>

    @GET("templates/{id}")
    suspend fun get(@Path("id") id: String): Response<TemplateResponse>
}

interface ProjectsApi {
    @POST("projects")
    suspend fun create(@Body request: ProjectCreateRequest): Response<ProjectResponseDto>

    @GET("projects")
    suspend fun list(): Response<List<ProjectResponseDto>>
}

interface BriefsApi {
    @PATCH("projects/{project_id}/brief")
    suspend fun update(@Path("project_id") projectId: String, @Body request: BriefUpdateRequest): Response<BriefResponseDto>

    @GET("projects/{project_id}/brief")
    suspend fun get(@Path("project_id") projectId: String): Response<BriefResponseDto>

    @POST("projects/{project_id}/brief/complete")
    suspend fun complete(@Path("project_id") projectId: String): Response<BriefResponseDto>
}

interface RecommendationsApi {
    @GET("projects/{project_id}/recommendations")
    suspend fun list(@Path("project_id") projectId: String): Response<List<RecommendationResponseDto>>

    @POST("projects/{project_id}/recommendations/select")
    suspend fun select(@Path("project_id") projectId: String, @Body request: RecommendationSelectRequest): Response<RecommendationResponseDto>
}

interface GenerationsApi {
    @POST("generations")
    suspend fun start(@Body request: StartGenerationRequest): Response<GenerationResponse>

    @GET("generations/{id}")
    suspend fun get(@Path("id") id: String): Response<GenerationResponse>
}

interface PaymentsApi {
    @POST("projects/{project_id}")
    suspend fun create(@Path("project_id") projectId: String, @Body request: PaymentCreateRequest): Response<PaymentResponse>

    @GET("{payment_id}")
    suspend fun get(@Path("payment_id") paymentId: String): Response<PaymentResponse>

    @GET("wallet")
    suspend fun wallet(): Response<WalletResponse>

    @GET("entitlements")
    suspend fun entitlements(): Response<List<EntitlementResponse>>

    @POST("entitlements/{entitlement_id}/consume")
    suspend fun consumeEntitlement(@Path("entitlement_id") entitlementId: String, @Body request: ConsumeEntitlementRequest = ConsumeEntitlementRequest()): Response<EntitlementResponse>
}

interface HolidaysApi {
    @GET("holidays")
    suspend fun list(@Query("kind") kind: String? = null): Response<List<HolidayResponseDto>>
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
}
