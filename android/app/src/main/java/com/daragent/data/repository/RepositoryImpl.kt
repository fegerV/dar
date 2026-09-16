package com.daragent.data.repository

import com.daragent.data.network.api.TemplatesApi
import com.daragent.data.network.dto.TemplateResponse
import com.daragent.domain.model.Template
import com.daragent.domain.repository.TemplateRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

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

private fun TemplateResponse.toDomain() = Template(
    id = id,
    title = title,
    category = category ?: "",
    previewUrl = null,
    priceRub = base_price_rub
)
