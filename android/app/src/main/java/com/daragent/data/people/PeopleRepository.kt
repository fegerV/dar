package com.daragent.data.people

import com.daragent.core.network.api.PeopleApi
import com.daragent.core.network.model.CreatePersonRequest
import com.daragent.core.network.model.PersonDto
import com.daragent.core.network.model.UpdatePersonRequest
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class PeopleRepository @Inject constructor(
    private val peopleApi: PeopleApi,
) {
    suspend fun getPeople(): Result<List<PersonDto>> {
        return runCatching {
            val response = peopleApi.getPeople()
            if (response.isSuccessful) {
                response.body() ?: emptyList()
            } else {
                throw Exception("Failed to get people: ${response.code()}")
            }
        }
    }

    suspend fun getPerson(id: String): Result<PersonDto> {
        return runCatching {
            val response = peopleApi.getPerson(id)
            if (response.isSuccessful) {
                response.body() ?: throw Exception("Empty body")
            } else {
                throw Exception("Failed to get person: ${response.code()}")
            }
        }
    }

    suspend fun createPerson(
        name: String,
        relationship: String?,
        birthDate: String?,
        interests: List<String>?,
        notes: String?,
    ): Result<PersonDto> {
        return runCatching {
            val request = CreatePersonRequest(
                name = name,
                relationship = relationship,
                birth_date = birthDate,
                interests = interests,
                notes = notes,
            )
            val response = peopleApi.createPerson(request)
            if (response.isSuccessful) {
                response.body() ?: throw Exception("Empty body")
            } else {
                throw Exception("Failed to create person: ${response.code()}")
            }
        }
    }

    suspend fun updatePerson(
        id: String,
        name: String?,
        relationship: String?,
        birthDate: String?,
        interests: List<String>?,
        notes: String?,
    ): Result<PersonDto> {
        return runCatching {
            val request = UpdatePersonRequest(
                name = name,
                relationship = relationship,
                birth_date = birthDate,
                interests = interests,
                notes = notes,
            )
            val response = peopleApi.updatePerson(id, request)
            if (response.isSuccessful) {
                response.body() ?: throw Exception("Empty body")
            } else {
                throw Exception("Failed to update person: ${response.code()}")
            }
        }
    }
}
