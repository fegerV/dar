package com.daragent.di

import com.daragent.data.repository.PeopleRepositoryImpl
import com.daragent.data.repository.TemplateRepositoryImpl
import com.daragent.domain.repository.PeopleRepository
import com.daragent.domain.repository.TemplateRepository
import com.daragent.presentation.home.HomeViewModel
import com.daragent.data.network.api.ApiModule

object ServiceLocator {
    val peopleRepository: PeopleRepository by lazy { PeopleRepositoryImpl(ApiModule.peopleApi) }
    val templateRepository: TemplateRepository by lazy { TemplateRepositoryImpl(ApiModule.templatesApi) }

    fun provideHomeViewModel(): HomeViewModel {
        return HomeViewModel(peopleRepository, templateRepository)
    }
}
