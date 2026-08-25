package com.daragent.data.di

import com.daragent.core.network.api.GenerationApi
import com.daragent.core.network.api.PeopleApi
import com.daragent.data.auth.AuthRepository
import com.daragent.data.generation.GenerationRepository
import com.daragent.data.people.PeopleRepository
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

    @Provides
    @Singleton
    fun providePeopleRepository(peopleApi: PeopleApi): PeopleRepository {
        return PeopleRepository(peopleApi)
    }

    @Provides
    @Singleton
    fun provideGenerationRepository(generationApi: GenerationApi): GenerationRepository {
        return GenerationRepository(generationApi)
    }
}
