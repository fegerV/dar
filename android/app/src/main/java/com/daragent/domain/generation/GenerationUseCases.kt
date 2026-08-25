package com.daragent.domain.generation

import com.daragent.data.generation.GenerationRepository
import com.daragent.core.network.model.GenerationDto
import javax.inject.Inject

class GetGenerationsUseCase @Inject constructor(
    private val generationRepository: GenerationRepository,
) {
    suspend operator fun invoke(status: String? = null): Result<List<GenerationDto>> {
        return generationRepository.getGenerations(status)
    }
}

class GetGenerationUseCase @Inject constructor(
    private val generationRepository: GenerationRepository,
) {
    suspend operator fun invoke(id: String): Result<GenerationDto> {
        return generationRepository.getGeneration(id)
    }
}

class CreateGenerationUseCase @Inject constructor(
    private val generationRepository: GenerationRepository,
) {
    suspend operator fun invoke(
        type: String,
        briefId: String?,
        photoUrl: String?,
    ): Result<GenerationDto> {
        return generationRepository.createGeneration(
            type = type,
            briefId = briefId,
            photoUrl = photoUrl,
        )
    }
}
