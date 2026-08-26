package com.daragent.domain.generation

import com.daragent.domain.model.Generation
import com.daragent.domain.repository.GenerationRepository
import javax.inject.Inject

class GetGenerationsUseCase @Inject constructor(
    private val generationRepository: GenerationRepository,
) {
    suspend operator fun invoke(): Result<List<Generation>> {
        return generationRepository.listGenerations()
    }
}

class GetGenerationUseCase @Inject constructor(
    private val generationRepository: GenerationRepository,
) {
    suspend operator fun invoke(id: String): Result<Generation> {
        return generationRepository.getGeneration(id)
    }
}

class CreateGenerationUseCase @Inject constructor(
    private val generationRepository: GenerationRepository,
) {
    suspend operator fun invoke(
        projectId: String,
        templateVersionId: String? = null,
    ): Result<Generation> {
        return generationRepository.createGeneration(
            projectId = projectId,
            templateVersionId = templateVersionId,
        )
    }
}
