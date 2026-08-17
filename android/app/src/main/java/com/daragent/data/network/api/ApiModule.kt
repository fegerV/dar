package com.daragent.data.network.api

import com.daragent.data.network.NetworkModule
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

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

interface GenerationsApi {
    @POST("generations")
    suspend fun start(@Body request: StartGenerationRequest): Response<GenerationResponse>

    @GET("generations/{id}")
    suspend fun get(@Path("id") id: String): Response<GenerationResponse>
}

interface PaymentsApi {
    @POST("payments")
    suspend fun create(@Body request: CreatePaymentRequest): Response<PaymentResponse>
}

object ApiModule {
    val authApi: AuthApi by lazy { NetworkModule.provideRetrofit().create(AuthApi::class.java) }
    val peopleApi: PeopleApi by lazy { NetworkModule.provideRetrofit().create(PeopleApi::class.java) }
    val templatesApi: TemplatesApi by lazy { NetworkModule.provideRetrofit().create(TemplatesApi::class.java) }
    val generationsApi: GenerationsApi by lazy { NetworkModule.provideRetrofit().create(GenerationsApi::class.java) }
    val paymentsApi: PaymentsApi by lazy { NetworkModule.provideRetrofit().create(PaymentsApi::class.java) }
}
