package com.daragent.data.repository

import com.daragent.core.network.api.PeopleApi
import com.daragent.core.network.model.CreatePersonRequest
import com.daragent.domain.model.Person
import com.daragent.domain.repository.PeopleRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class PeopleRepositoryImpl(
    private val peopleApi: PeopleApi,
) : PeopleRepository {

    override suspend fun list(): Result<List<Person>> =
        withContext(Dispatchers.IO) {
            runCatching {
                val response = peopleApi.getPeople()
                if (response.isSuccessful) {
                    response.body().orEmpty().map { it.toDomain() }
                } else {
                    throw Exception("Failed to get people: ${response.code()}")
                }
            }
        }

    override suspend fun create(person: Person): Result<Person> =
        withContext(Dispatchers.IO) {
            runCatching {
                val request = CreatePersonRequest(
                    name = person.name,
                    relationship = person.relationship,
                    birth_date = person.birthDate,
                    interests = person.interests,
                    notes = null,
                )
                val response = peopleApi.createPerson(request)
                if (response.isSuccessful) {
                    response.body()!!.toDomain()
                } else {
                    throw Exception("Failed to create person: ${response.code()}")
                }
            }
        }

    override suspend fun get(id: String): Result<Person> =
        withContext(Dispatchers.IO) {
            runCatching {
                val response = peopleApi.getPerson(id)
                if (response.isSuccessful) {
                    response.body()!!.toDomain()
                } else {
                    throw Exception("Failed to get person: ${response.code()}")
                }
            }
        }

    private fun com.daragent.core.network.model.PersonDto.toDomain() = Person(
        id = id,
        name = name,
        relationship = relationship,
        birthDate = birth_date,
        interests = interests.orEmpty(),
        traits = traits.orEmpty()
    )
}
