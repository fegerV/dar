package com.daragent.data.repository

import com.daragent.data.network.api.PeopleApi
import com.daragent.data.network.api.TemplatesApi
import com.daragent.data.network.dto.CreatePersonRequest
import com.daragent.data.network.dto.TemplateListResponse
import com.daragent.data.network.dto.TemplateResponse
import com.daragent.domain.model.Person
import com.daragent.domain.model.Template
import com.daragent.domain.repository.PeopleRepository
import com.daragent.domain.repository.TemplateRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class PeopleRepositoryImpl(private val api: PeopleApi) : PeopleRepository {
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
    traits = traits
)

private fun TemplateResponse.toDomain() = Template(
    id = id,
    title = title,
    category = category ?: "",
    previewUrl = null,
    priceRub = base_price_rub
)
