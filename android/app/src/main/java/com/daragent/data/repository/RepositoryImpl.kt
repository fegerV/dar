package com.daragent.data.repository

import com.daragent.data.network.api.PeopleApi
import com.daragent.data.network.api.TemplatesApi
import com.daragent.data.network.dto.CreatePersonRequest
import com.daragent.data.network.dto.TemplateResponse
import com.daragent.domain.model.Person
import com.daragent.domain.model.Template
import com.daragent.domain.repository.PeopleRepository
import com.daragent.domain.repository.TemplateRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * People repository on the legacy data/network stack (ApiModule, `recipients` routes).
 * The Hilt graph binds PeopleRepositoryImpl.kt instead, which is built on core/network's
 * PeopleApi. Both exist because the two network stacks have not been merged yet, and both
 * callers (RepositoryModule and ServiceLocator) need a concrete PeopleRepository.
 */
class LegacyPeopleRepositoryImpl(private val api: PeopleApi) : PeopleRepository {
    override suspend fun list(): Result<List<Person>> =
        withContext(Dispatchers.IO) {
            runCatching { api.list().body()?.items?.map { it.toDomain() }.orEmpty() }
        }

    override suspend fun create(person: Person): Result<Person> =
        withContext(Dispatchers.IO) {
            runCatching {
                api.create(
                    CreatePersonRequest(
                        firstName = person.name,
                        relationship = person.relationship,
                        birthDate = person.birthDate,
                        interests = person.interests,
                        traits = person.traits
                    )
                ).body()!!.toDomain()
            }
        }

    override suspend fun get(id: String): Result<Person> =
        withContext(Dispatchers.IO) {
            runCatching { api.get(id).body()!!.toDomain() }
        }
}

class TemplateRepositoryImpl(private val api: TemplatesApi) : TemplateRepository {
    override suspend fun list(): Result<List<Template>> =
        withContext(Dispatchers.IO) {
            runCatching { api.list().body()?.items?.map { it.toDomain() }.orEmpty() }
        }

    override suspend fun get(id: String): Result<Template> =
        withContext(Dispatchers.IO) {
            runCatching { api.get(id).body()!!.toDomain() }
        }
}

private fun com.daragent.data.network.dto.PersonResponse.toDomain() = Person(
    id = id,
    name = "${firstName ?: ""} ${lastName ?: ""}".trim(),
    relationship = relationship,
    birthDate = birthDate,
    interests = interests,
    traits = traits,
    // The legacy recipients payload carries no photo_url, unlike core.network's PersonDto.
    photoUrl = null
)

private fun TemplateResponse.toDomain() = Template(
    id = id,
    title = title,
    category = category ?: "",
    previewUrl = null,
    priceRub = base_price_rub
)
