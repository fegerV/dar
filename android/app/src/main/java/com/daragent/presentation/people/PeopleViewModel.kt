package com.daragent.presentation.people

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.daragent.core.network.model.PersonDto
import com.daragent.domain.conversation.CreatePersonUseCase
import com.daragent.domain.conversation.GetPeopleUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class PeopleUiState(
    val people: List<PersonDto> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val showCreateDialog: Boolean = false,
    val createName: String = "",
    val createRelationship: String = "",
    val createBirthDate: String = "",
    val createInterests: String = "",
    val createNotes: String = "",
    val isCreating: Boolean = false,
)

@HiltViewModel
class PeopleViewModel @Inject constructor(
    private val getPeopleUseCase: GetPeopleUseCase,
    private val createPersonUseCase: CreatePersonUseCase,
) : ViewModel() {

    private val _uiState = MutableStateFlow(PeopleUiState())
    val uiState: StateFlow<PeopleUiState> = _uiState.asStateFlow()

    init {
        loadPeople()
    }

    fun loadPeople() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            getPeopleUseCase().fold(
                onSuccess = { people ->
                    _uiState.update {
                        it.copy(people = people, isLoading = false)
                    }
                },
                onFailure = { error ->
                    _uiState.update {
                        it.copy(isLoading = false, error = error.message)
                    }
                }
            )
        }
    }

    fun showCreateDialog() {
        _uiState.update {
            it.copy(
                showCreateDialog = true,
                createName = "",
                createRelationship = "",
                createBirthDate = "",
                createInterests = "",
                createNotes = "",
            )
        }
    }

    fun hideCreateDialog() {
        _uiState.update { it.copy(showCreateDialog = false) }
    }

    fun updateCreateName(name: String) {
        _uiState.update { it.copy(createName = name) }
    }

    fun updateCreateRelationship(relationship: String) {
        _uiState.update { it.copy(createRelationship = relationship) }
    }

    fun updateCreateBirthDate(birthDate: String) {
        _uiState.update { it.copy(createBirthDate = birthDate) }
    }

    fun updateCreateInterests(interests: String) {
        _uiState.update { it.copy(createInterests = interests) }
    }

    fun updateCreateNotes(notes: String) {
        _uiState.update { it.copy(createNotes = notes) }
    }

    fun createPerson() {
        val state = _uiState.value
        if (state.createName.isBlank()) return

        viewModelScope.launch {
            _uiState.update { it.copy(isCreating = true) }

            val interests = state.createInterests
                .split(",")
                .map { it.trim() }
                .filter { it.isNotBlank() }
                .takeIf { it.isNotEmpty() }

            createPersonUseCase(
                name = state.createName.trim(),
                relationship = state.createRelationship.trim().takeIf { it.isNotBlank() },
                birthDate = state.createBirthDate.trim().takeIf { it.isNotBlank() },
                interests = interests,
                notes = state.createNotes.trim().takeIf { it.isNotBlank() },
            ).fold(
                onSuccess = { person ->
                    _uiState.update {
                        it.copy(
                            people = it.people + person,
                            showCreateDialog = false,
                            isCreating = false,
                        )
                    }
                },
                onFailure = { error ->
                    _uiState.update {
                        it.copy(isCreating = false, error = error.message)
                    }
                }
            )
        }
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}
