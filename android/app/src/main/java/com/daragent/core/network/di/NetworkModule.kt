package com.daragent.core.network.di

import com.daragent.core.network.*
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideRetrofitClient(authInterceptor: AuthInterceptor): RetrofitClient {
        return RetrofitClient(authInterceptor)
    }

    @Provides
    @Singleton
    fun provideAuthApi(retrofitClient: RetrofitClient): AuthApi {
        return retrofitClient.retrofit.create(AuthApi::class.java)
    }

    @Provides
    @Singleton
    fun provideUserApi(retrofitClient: RetrofitClient): UserApi {
        return retrofitClient.retrofit.create(UserApi::class.java)
    }

    @Provides
    @Singleton
    fun providePeopleApi(retrofitClient: RetrofitClient): PeopleApi {
        return retrofitClient.retrofit.create(PeopleApi::class.java)
    }

    @Provides
    @Singleton
    fun provideConversationApi(retrofitClient: RetrofitClient): ConversationApi {
        return retrofitClient.retrofit.create(ConversationApi::class.java)
    }

    @Provides
    @Singleton
    fun provideBriefApi(retrofitClient: RetrofitClient): BriefApi {
        return retrofitClient.retrofit.create(BriefApi::class.java)
    }

    @Provides
    @Singleton
    fun provideMediaApi(retrofitClient: RetrofitClient): MediaApi {
        return retrofitClient.retrofit.create(MediaApi::class.java)
    }

    @Provides
    @Singleton
    fun provideGenerationApi(retrofitClient: RetrofitClient): GenerationApi {
        return retrofitClient.retrofit.create(GenerationApi::class.java)
    }

    @Provides
    @Singleton
    fun providePaymentApi(retrofitClient: RetrofitClient): PaymentApi {
        return retrofitClient.retrofit.create(PaymentApi::class.java)
    }

    @Provides
    @Singleton
    fun provideWalletApi(retrofitClient: RetrofitClient): WalletApi {
        return retrofitClient.retrofit.create(WalletApi::class.java)
    }

    @Provides
    @Singleton
    fun provideReferralApi(retrofitClient: RetrofitClient): ReferralApi {
        return retrofitClient.retrofit.create(ReferralApi::class.java)
    }

    @Provides
    @Singleton
    fun provideFeedbackApi(retrofitClient: RetrofitClient): FeedbackApi {
        return retrofitClient.retrofit.create(FeedbackApi::class.java)
    }
}
