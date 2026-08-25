package com.daragent.domain.di

import com.daragent.data.auth.AuthRepository
import com.daragent.data.chat.ChatRepository
import com.daragent.data.generation.GenerationRepository
import com.daragent.data.payment.PaymentRepository
import com.daragent.data.people.PeopleRepository
import com.daragent.domain.auth.*
import com.daragent.domain.chat.*
import com.daragent.domain.conversation.*
import com.daragent.domain.generation.*
import com.daragent.domain.payment.*
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

    @Provides
    @Singleton
    fun provideSendMessageUseCase(chatRepository: ChatRepository): SendMessageUseCase {
        return SendMessageUseCase(chatRepository)
    }

    @Provides
    @Singleton
    fun provideCreateProjectUseCase(chatRepository: ChatRepository): CreateProjectUseCase {
        return CreateProjectUseCase(chatRepository)
    }

    @Provides
    @Singleton
    fun provideGetProjectUseCase(chatRepository: ChatRepository): GetProjectUseCase {
        return GetProjectUseCase(chatRepository)
    }

    @Provides
    @Singleton
    fun provideCreatePaymentUseCase(paymentRepository: PaymentRepository): CreatePaymentUseCase {
        return CreatePaymentUseCase(paymentRepository)
    }

    @Provides
    @Singleton
    fun provideGetPaymentStatusUseCase(paymentRepository: PaymentRepository): GetPaymentStatusUseCase {
        return GetPaymentStatusUseCase(paymentRepository)
    }

    @Provides
    @Singleton
    fun provideGetPaymentsUseCase(paymentRepository: PaymentRepository): GetPaymentsUseCase {
        return GetPaymentsUseCase(paymentRepository)
    }
}
