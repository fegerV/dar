package com.daragent.data.repository

import com.daragent.data.network.api.PeopleApi
import com.daragent.data.network.dto.CreatePersonRequest
import com.daragent.data.network.dto.PersonResponse
import com.daragent.domain.model.Person
import com.daragent.domain.repository.PeopleRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Legacy implementation of PeopleRepository that uses the old data.network.api.PeopleApi.
 * This is required by ServiceLocator for backward compatibility.
 * 
 * Note: There is also PeopleRepositoryImpl in com.daragent.data.repository package
 * which uses core.network.PeopleApi for Hilt-based dependency injection.
 */
class LegacyPeopleRepositoryImpl(
    private val api: PeopleApi,
) : PeopleRepository {

    override suspend fun list(): Result<List<Person>> = withContext(Dispatchers.IO) {
        runCatching {
            val response = api.list()
            if (response.isSuccessful) {
                response.body()?.items?.map { it.toDomain() }.orEmpty()
            } else {
                throw Exception("Failed to list people: ${response.code()}")
            }
        }
    }

    override suspend fun create(person: Person): Result<Person> = withContext(Dispatchers.IO) {
        runCatching {
            val request = CreatePersonRequest(
                firstName = person.name,
                relationship = person.relationship,
                birthDate = person.birthDate,
                interests = person.interests,
                traits = person.traits,
            )
            val response = api.create(request)
            if (response.isSuccessful) {
                response.body()?.toDomain() ?: throw Exception("Empty response body")
            } else {
                throw Exception("Failed to create person: ${response.code()}")
            }
        }
    }

    override suspend fun get(id: String): Result<Person> = withContext(Dispatchers.IO) {
        runCatching {
            val response = api.get(id)
            if (response.isSuccessful) {
                response.body()?.toDomain() ?: throw Exception("Empty response body")
            } else {
                throw Exception("Failed to get person: ${response.code()}")
            }
        }
    }

    private fun PersonResponse.toDomain() = Person(
        id = id,
        name = nickname ?: "${firstName.orEmpty()} ${lastName.orEmpty()}".trim().ifEmpty { "Unknown" },
        relationship = relationship,
        birthDate = birthDate,
        interests = interests,
        traits = traits,
        photoUrl = null
    )
}
