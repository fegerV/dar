package com.daragent.domain.conversation

import com.daragent.domain.model.Person
import com.daragent.domain.repository.PeopleRepository
import javax.inject.Inject

class GetPeopleUseCase @Inject constructor(
    private val peopleRepository: PeopleRepository,
) {
    suspend operator fun invoke(): Result<List<Person>> {
        return peopleRepository.list()
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
    ): Result<Person> {
        val person = Person(
            id = "",
            name = name,
            relationship = relationship,
            birthDate = birthDate,
            interests = interests.orEmpty(),
            traits = emptyList()
        )
        return peopleRepository.create(person)
    }
}

class GetPersonUseCase @Inject constructor(
    private val peopleRepository: PeopleRepository,
) {
    suspend operator fun invoke(id: String): Result<Person> {
        return peopleRepository.get(id)
    }
}
