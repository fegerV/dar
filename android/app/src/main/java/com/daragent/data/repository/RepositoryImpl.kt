package com.daragent.data.repository

import com.daragent.data.network.api.PeopleApi
import com.daragent.data.network.api.TemplatesApi
import com.daragent.domain.model.Person
import com.daragent.domain.model.Template
import com.daragent.domain.repository.PeopleRepository
import com.daragent.domain.repository.TemplateRepository

class PeopleRepositoryImpl(private val api: PeopleApi) : PeopleRepository {
    override suspend fun list() = runCatching { api.list().body().orEmpty() }
    override suspend fun create(person: Person) = runCatching { api.create(person).body()!! }
}

class TemplateRepositoryImpl(private val api: TemplatesApi) : TemplateRepository {
    override suspend fun list() = runCatching { api.list().body().orEmpty() }
    override suspend fun get(id: String) = runCatching { api.get(id).body()!! }
}
