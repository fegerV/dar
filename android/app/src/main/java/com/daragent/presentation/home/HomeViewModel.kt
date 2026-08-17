package com.daragent.presentation.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.daragent.domain.model.Person
import com.daragent.domain.model.Template
import com.daragent.domain.repository.PeopleRepository
import com.daragent.domain.repository.TemplateRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class HomeState(
    val people: List<Person> = emptyList(),
    val templates: List<Template> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

class HomeViewModel(
    private val peopleRepository: PeopleRepository,
    private val templateRepository: TemplateRepository
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
                _state.value = _state.value.copy(people = people, templates = templates, isLoading = false)
            } catch (e: Exception) {
                _state.value = _state.value.copy(error = e.message, isLoading = false)
            }
        }
    }
}
