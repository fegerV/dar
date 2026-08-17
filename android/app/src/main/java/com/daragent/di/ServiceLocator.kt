package com.daragent.di

import com.daragent.data.repository.PeopleRepositoryImpl
import com.daragent.data.repository.PaymentRepositoryImpl
import com.daragent.data.repository.ProjectRepositoryImpl
import com.daragent.data.repository.TemplateRepositoryImpl
import com.daragent.domain.repository.PeopleRepository
import com.daragent.domain.repository.PaymentRepository
import com.daragent.domain.repository.ProjectRepository
import com.daragent.domain.repository.TemplateRepository
import com.daragent.presentation.creategreeting.CreateGreetingViewModel
import com.daragent.presentation.home.HomeViewModel
import com.daragent.presentation.payment.PaymentViewModel
import com.daragent.data.network.api.ApiModule

object ServiceLocator {
    val peopleRepository: PeopleRepository by lazy { PeopleRepositoryImpl(ApiModule.peopleApi) }
    val templateRepository: TemplateRepository by lazy { TemplateRepositoryImpl(ApiModule.templatesApi) }
    val projectRepository: ProjectRepository by lazy { ProjectRepositoryImpl(ApiModule.projectsApi, ApiModule.briefsApi, ApiModule.recommendationsApi, ApiModule.holidaysApi, ApiModule.generationsApi) }
    val paymentRepository: PaymentRepository by lazy { PaymentRepositoryImpl(ApiModule.paymentsApi) }

    fun provideHomeViewModel(): HomeViewModel {
        return HomeViewModel(peopleRepository, templateRepository)
    }

    fun provideCreateGreetingViewModel(): CreateGreetingViewModel {
        return CreateGreetingViewModel(peopleRepository, projectRepository, templateRepository)
    }

    fun providePaymentViewModel(): PaymentViewModel {
        return PaymentViewModel(paymentRepository)
    }
}
