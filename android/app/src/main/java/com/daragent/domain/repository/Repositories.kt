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

interface AuthRepository {
    suspend fun login(email: String, password: String): Result<AuthTokens>
    suspend fun register(email: String, password: String, displayName: String?): Result<AuthTokens>
    suspend fun me(): Result<UserProfile>
    fun getAccessToken(): String?
    fun clearTokens()
}
