package com.daragent.di

import com.daragent.data.local.AuthTokenManager
import com.daragent.data.local.DarAgentDatabase
import com.daragent.data.repository.AuthRepositoryImpl
import com.daragent.data.repository.DeliveryRepositoryImpl
import com.daragent.data.repository.PeopleRepositoryImpl
import com.daragent.data.repository.PaymentRepositoryImpl
import com.daragent.data.repository.ProjectRepositoryImpl
import com.daragent.data.repository.ReferralRepositoryImpl
import com.daragent.data.repository.FeedbackRepositoryImpl
import com.daragent.data.repository.TemplateRepositoryImpl
import com.daragent.data.repository.local.LocalCacheRepository
import com.daragent.data.network.api.ApiModule
import com.daragent.domain.repository.AuthRepository
import com.daragent.domain.repository.DeliveryRepository
import com.daragent.domain.repository.FeedbackRepository
import com.daragent.domain.repository.PeopleRepository
import com.daragent.domain.repository.PaymentRepository
import com.daragent.domain.repository.ProjectRepository
import com.daragent.domain.repository.ReferralRepository
import com.daragent.domain.repository.TemplateRepository
import com.daragent.presentation.creategreeting.CreateGreetingViewModel
import com.daragent.presentation.history.HistoryViewModel
import com.daragent.presentation.home.HomeViewModel
import com.daragent.presentation.mascot.MascotRepository
import com.daragent.presentation.payment.PaymentViewModel
import com.daragent.presentation.profile.ProfileViewModel

object ServiceLocator {
    val database: DarAgentDatabase by lazy { com.daragent.DarAgentApp.database }
    val peopleRepository: PeopleRepository by lazy { PeopleRepositoryImpl(ApiModule.peopleApi) }
    val templateRepository: TemplateRepository by lazy { TemplateRepositoryImpl(ApiModule.templatesApi) }
    val projectRepository: ProjectRepository by lazy { ProjectRepositoryImpl(ApiModule.projectsApi, ApiModule.briefsApi, ApiModule.recommendationsApi, ApiModule.holidaysApi, ApiModule.generationsApi) }
    val paymentRepository: PaymentRepository by lazy { PaymentRepositoryImpl(ApiModule.paymentsApi) }
    val deliveryRepository: DeliveryRepository by lazy { DeliveryRepositoryImpl(ApiModule.deliveriesApi) }
    val authRepository: AuthRepository by lazy { AuthRepositoryImpl(ApiModule.authApi, AuthTokenManager) }
    val localCacheRepository: LocalCacheRepository by lazy { LocalCacheRepository(database) }
    val referralRepository: ReferralRepository by lazy { ReferralRepositoryImpl(ApiModule.referralsApi) }
    val feedbackRepository: FeedbackRepository by lazy { FeedbackRepositoryImpl(ApiModule.feedbackApi) }
    val mascotRepository: MascotRepository by lazy { MascotRepository() }

    fun provideHomeViewModel(): HomeViewModel {
        return HomeViewModel(peopleRepository, templateRepository, authRepository)
    }

    fun provideCreateGreetingViewModel(): CreateGreetingViewModel {
        return CreateGreetingViewModel(peopleRepository, projectRepository, templateRepository)
    }

    fun providePaymentViewModel(): PaymentViewModel {
        return PaymentViewModel(paymentRepository)
    }

    fun provideProfileViewModel(): ProfileViewModel {
        return ProfileViewModel(authRepository, paymentRepository)
    }

    fun provideHistoryViewModel(): HistoryViewModel {
        return HistoryViewModel(projectRepository)
    }
}
