package com.daragent.domain.repository

import com.daragent.domain.model.Person
import com.daragent.domain.model.Template

interface PeopleRepository {
    suspend fun list(): Result<List<Person>>
    suspend fun create(person: Person): Result<Person>
}

interface TemplateRepository {
    suspend fun list(): Result<List<Template>>
    suspend fun get(id: String): Result<Template>
}
