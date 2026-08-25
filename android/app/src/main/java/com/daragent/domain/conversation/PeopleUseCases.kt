package com.daragent.domain.conversation

import com.daragent.data.people.PeopleRepository
import com.daragent.core.network.model.PersonDto
import javax.inject.Inject

class GetPeopleUseCase @Inject constructor(
    private val peopleRepository: PeopleRepository,
) {
    suspend operator fun invoke(): Result<List<PersonDto>> {
        return peopleRepository.getPeople()
    }
}

class CreatePersonUseCase @Inject constructor(
    private val peopleRepository: PeopleRepository,
) {
    suspend operator fun invoke(
        name: String,
        relationship: String?,
        birthDate: String?,
        interests: List<String>?,
        notes: String?,
    ): Result<PersonDto> {
        return peopleRepository.createPerson(
            name = name,
            relationship = relationship,
            birthDate = birthDate,
            interests = interests,
            notes = notes,
        )
    }
}

class GetPersonUseCase @Inject constructor(
    private val peopleRepository: PeopleRepository,
) {
    suspend operator fun invoke(id: String): Result<PersonDto> {
        return peopleRepository.getPerson(id)
    }
}
