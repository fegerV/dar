package com.daragent.data.di

import com.daragent.core.network.AuthApi
import com.daragent.core.network.PeopleApi
import com.daragent.core.network.api.ChatApi
import com.daragent.core.network.GenerationApi
import com.daragent.data.network.api.ApiModule
import com.daragent.data.network.api.PaymentsApi
import com.daragent.data.auth.AuthRepository
import com.daragent.data.generation.GenerationRepository
import com.daragent.data.payment.PaymentRepository
import com.daragent.data.people.PeopleRepository
import com.daragent.data.repository.ChatRepositoryImpl
import com.daragent.data.repository.GenerationRepositoryImpl
import com.daragent.data.repository.PaymentRepositoryImpl
import com.daragent.data.repository.PeopleRepositoryImpl
import com.daragent.domain.repository.ChatRepository
import com.daragent.domain.repository.GenerationRepository as GenerationRepositoryInterface
import com.daragent.domain.repository.PaymentRepository as PaymentRepositoryInterface
import com.daragent.domain.repository.PeopleRepository as PeopleRepositoryInterface
import com.daragent.core.security.TokenManager
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object RepositoryModule {

    @Provides
    @Singleton
    fun provideAuthRepository(authApi: AuthApi, tokenManager: TokenManager): AuthRepository {
        return AuthRepository(authApi, tokenManager)
    }

    @Provides
    @Singleton
    fun providePeopleRepository(peopleApi: PeopleApi): PeopleRepositoryInterface {
        return PeopleRepositoryImpl(peopleApi)
    }

    @Provides
    @Singleton
    fun provideChatRepository(chatApi: ChatApi): ChatRepository {
        return ChatRepositoryImpl(chatApi)
    }

    @Provides
    @Singleton
    fun provideGenerationRepository(generationApi: GenerationApi): GenerationRepositoryInterface {
        return GenerationRepositoryImpl(generationApi)
    }

    // The complete implementation of the domain PaymentRepository interface lives in
    // data/repository/PaymentRepositoryImpl.kt and is built on the legacy PaymentsApi
    // (payments/projects/{id}, payments/{id}, payments/wallet, payments/entitlements).
    // Those paths match the real backend routes, unlike core/network's PaymentApi, and
    // core/network has no entitlements endpoint at all — so the legacy API is what the
    // domain interface can actually be satisfied with.
    @Provides
    @Singleton
    fun providePaymentsApi(): PaymentsApi = ApiModule.paymentsApi

    @Provides
    @Singleton
    fun providePaymentRepository(paymentsApi: PaymentsApi): PaymentRepositoryInterface {
        return PaymentRepositoryImpl(paymentsApi)
    }
}
