package com.daragent.presentation.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.daragent.di.ServiceLocator
import com.daragent.domain.model.Person
import com.daragent.domain.model.Template
import com.daragent.domain.model.UserProfile
import com.daragent.domain.repository.AuthRepository
import com.daragent.domain.repository.PeopleRepository
import com.daragent.domain.repository.TemplateRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class HomeState(
    val people: List<Person> = emptyList(),
    val templates: List<Template> = emptyList(),
    val user: UserProfile? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)

class HomeViewModel(
    private val peopleRepository: PeopleRepository = ServiceLocator.peopleRepository,
    private val templateRepository: TemplateRepository = ServiceLocator.templateRepository,
    private val authRepository: AuthRepository = ServiceLocator.authRepository
) : ViewModel() {
    private val _state = MutableStateFlow(HomeState())
    val state: StateFlow<HomeState> = _state

    init {
        loadHome()
    }

    fun loadHome() {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true, error = null)
            try {
                val people = peopleRepository.list().getOrNull().orEmpty()
                val templates = templateRepository.list().getOrNull().orEmpty()
                val user = authRepository.me().getOrNull()
                _state.value = _state.value.copy(
                    people = people,
                    templates = templates,
                    user = user,
                    isLoading = false
                )
            } catch (e: Exception) {
                _state.value = _state.value.copy(error = e.message, isLoading = false)
            }
        }
    }
}
