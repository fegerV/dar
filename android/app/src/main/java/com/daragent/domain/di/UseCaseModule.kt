package com.daragent.domain.di

import com.daragent.data.auth.AuthRepository
import com.daragent.data.people.PeopleRepository
import com.daragent.data.generation.GenerationRepository
import com.daragent.domain.auth.*
import com.daragent.domain.conversation.*
import com.daragent.domain.generation.*
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object UseCaseModule {

    @Provides
    @Singleton
    fun provideLoginUseCase(authRepository: AuthRepository): LoginUseCase {
        return LoginUseCase(authRepository)
    }

    @Provides
    @Singleton
    fun provideRegisterUseCase(authRepository: AuthRepository): RegisterUseCase {
        return RegisterUseCase(authRepository)
    }

    @Provides
    @Singleton
    fun provideLogoutUseCase(authRepository: AuthRepository): LogoutUseCase {
        return LogoutUseCase(authRepository)
    }

    @Provides
    @Singleton
    fun provideIsLoggedInUseCase(authRepository: AuthRepository): IsLoggedInUseCase {
        return IsLoggedInUseCase(authRepository)
    }

    @Provides
    @Singleton
    fun provideGetPeopleUseCase(peopleRepository: PeopleRepository): GetPeopleUseCase {
        return GetPeopleUseCase(peopleRepository)
    }

    @Provides
    @Singleton
    fun provideCreatePersonUseCase(peopleRepository: PeopleRepository): CreatePersonUseCase {
        return CreatePersonUseCase(peopleRepository)
    }

    @Provides
    @Singleton
    fun provideGetPersonUseCase(peopleRepository: PeopleRepository): GetPersonUseCase {
        return GetPersonUseCase(peopleRepository)
    }

    @Provides
    @Singleton
    fun provideGetGenerationsUseCase(generationRepository: GenerationRepository): GetGenerationsUseCase {
        return GetGenerationsUseCase(generationRepository)
    }

    @Provides
    @Singleton
    fun provideGetGenerationUseCase(generationRepository: GenerationRepository): GetGenerationUseCase {
        return GetGenerationUseCase(generationRepository)
    }

    @Provides
    @Singleton
    fun provideCreateGenerationUseCase(generationRepository: GenerationRepository): CreateGenerationUseCase {
        return CreateGenerationUseCase(generationRepository)
    }
}
