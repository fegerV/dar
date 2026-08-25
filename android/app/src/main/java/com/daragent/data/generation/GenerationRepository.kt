package com.daragent.data.generation

import com.daragent.core.network.api.GenerationApi
import com.daragent.core.network.model.CreateGenerationRequest
import com.daragent.core.network.model.GenerationDto
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class GenerationRepository @Inject constructor(
    private val generationApi: GenerationApi,
) {
    suspend fun getGenerations(status: String? = null): Result<List<GenerationDto>> {
        return runCatching {
            val response = generationApi.getGenerations(status)
            if (response.isSuccessful) {
                response.body() ?: emptyList()
            } else {
                throw Exception("Failed to get generations: ${response.code()}")
            }
        }
    }

    suspend fun getGeneration(id: String): Result<GenerationDto> {
        return runCatching {
            val response = generationApi.getGeneration(id)
            if (response.isSuccessful) {
                response.body() ?: throw Exception("Empty body")
            } else {
                throw Exception("Failed to get generation: ${response.code()}")
            }
        }
    }

    suspend fun createGeneration(
        type: String,
        briefId: String?,
        photoUrl: String?,
    ): Result<GenerationDto> {
        return runCatching {
            val request = CreateGenerationRequest(
                type = type,
                brief_id = briefId,
                photo_url = photoUrl,
            )
            val response = generationApi.createGeneration(request)
            if (response.isSuccessful) {
                response.body() ?: throw Exception("Empty body")
            } else {
                throw Exception("Failed to create generation: ${response.code()}")
            }
        }
    }
}
