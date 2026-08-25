package com.daragent.data.di

import com.daragent.data.auth.AuthRepository
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
    fun provideAuthRepository(tokenManager: TokenManager): AuthRepository {
        return AuthRepository(tokenManager)
    }
}
