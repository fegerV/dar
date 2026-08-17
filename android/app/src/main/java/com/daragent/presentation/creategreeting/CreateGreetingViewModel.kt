package com.daragent.presentation.creategreeting

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.daragent.domain.model.Brief
import com.daragent.domain.model.Occasion
import com.daragent.domain.model.Person
import com.daragent.domain.model.Project
import com.daragent.domain.model.Recommendation
import com.daragent.domain.model.Template
import com.daragent.domain.repository.PeopleRepository
import com.daragent.domain.repository.ProjectRepository
import com.daragent.domain.repository.TemplateRepository
import com.daragent.di.ServiceLocator
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class CreateGreetingState(
    val step: FlowStep = FlowStep.SELECT_PERSON,
    val people: List<Person> = emptyList(),
    val occasions: List<Occasion> = emptyList(),
    val recommendations: List<Recommendation> = emptyList(),
    val templates: List<Template> = emptyList(),
    val selectedPerson: Person? = null,
    val selectedOccasion: Occasion? = null,
    val project: Project? = null,
    val brief: Brief? = null,
    val selectedRecommendation: Recommendation? = null,
    val selectedTemplate: Template? = null,
    val generation: com.daragent.domain.model.Generation? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)

enum class FlowStep {
    SELECT_PERSON,
    SELECT_OCCASION,
    FILL_BRIEF,
    RECOMMENDATIONS,
    SELECT_TEMPLATE,
    GENERATION
}

class CreateGreetingViewModel(
    peopleRepository: PeopleRepository? = null,
    projectRepository: ProjectRepository? = null,
    templateRepository: TemplateRepository? = null
) : ViewModel() {
    private val peopleRepo = peopleRepository ?: ServiceLocator.peopleRepository
    private val projectRepo = projectRepository ?: ServiceLocator.projectRepository
    private val templateRepo = templateRepository ?: ServiceLocator.templateRepository

    private val _state = MutableStateFlow(CreateGreetingState())
    val state: StateFlow<CreateGreetingState> = _state

    init {
        loadPeople()
        loadOccasions()
    }

    fun loadPeople() {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true, error = null)
            val people = peopleRepo.list().getOrNull().orEmpty()
            _state.value = _state.value.copy(people = people, isLoading = false)
        }
    }

    fun loadOccasions() {
        viewModelScope.launch {
            val occasions = projectRepo.listOccasions().getOrNull().orEmpty()
            _state.value = _state.value.copy(occasions = occasions)
        }
    }

    fun selectPerson(person: Person) {
        _state.value = _state.value.copy(selectedPerson = person, step = FlowStep.SELECT_OCCASION)
    }

    fun selectOccasion(occasion: Occasion) {
        val person = _state.value.selectedPerson ?: return
        _state.value = _state.value.copy(isLoading = true, error = null)
        viewModelScope.launch {
            val result = projectRepo.create(person.id, occasion.code, occasion.title, null)
            result.onSuccess { project ->
                _state.value = _state.value.copy(
                    project = project,
                    selectedOccasion = occasion,
                    step = FlowStep.FILL_BRIEF,
                    isLoading = false
                )
            }.onFailure { e ->
                _state.value = _state.value.copy(error = e.message, isLoading = false)
            }
        }
    }

    fun updateBrief(brief: Brief) {
        val project = _state.value.project ?: return
        _state.value = _state.value.copy(isLoading = true, error = null)
        viewModelScope.launch {
            val result = projectRepo.updateBrief(project.id, brief)
            result.onSuccess { updated ->
                _state.value = _state.value.copy(brief = updated, isLoading = false)
            }.onFailure { e ->
                _state.value = _state.value.copy(error = e.message, isLoading = false)
            }
        }
    }

    fun completeBrief() {
        val project = _state.value.project ?: return
        _state.value = _state.value.copy(isLoading = true, error = null)
        viewModelScope.launch {
            val result = projectRepo.completeBrief(project.id)
            result.onSuccess { brief ->
                _state.value = _state.value.copy(brief = brief, step = FlowStep.RECOMMENDATIONS, isLoading = false)
                loadRecommendations(project.id)
            }.onFailure { e ->
                _state.value = _state.value.copy(error = e.message, isLoading = false)
            }
        }
    }

    fun loadRecommendations(projectId: String) {
        viewModelScope.launch {
            val result = projectRepo.getRecommendations(projectId)
            result.onSuccess { recs ->
                _state.value = _state.value.copy(recommendations = recs)
            }.onFailure { e ->
                _state.value = _state.value.copy(error = e.message)
            }
        }
    }

    fun selectRecommendation(recommendation: Recommendation) {
        val project = _state.value.project ?: return
        _state.value = _state.value.copy(isLoading = true, error = null)
        viewModelScope.launch {
            val result = projectRepo.selectRecommendation(project.id, recommendation.id)
            result.onSuccess { selected ->
                _state.value = _state.value.copy(
                    selectedRecommendation = selected,
                    step = FlowStep.SELECT_TEMPLATE,
                    isLoading = false
                )
            }.onFailure { e ->
                _state.value = _state.value.copy(error = e.message, isLoading = false)
            }
        }
    }

    fun loadTemplates() {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true, error = null)
            val templates = templateRepo.list().getOrNull().orEmpty()
            _state.value = _state.value.copy(templates = templates, isLoading = false)
        }
    }

    fun selectTemplate(template: Template) {
        _state.value = _state.value.copy(selectedTemplate = template, step = FlowStep.GENERATION)
    }
}
