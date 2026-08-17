package com.daragent.data.repository

import com.daragent.data.network.api.GenerationsApi
import com.daragent.data.network.api.HolidaysApi
import com.daragent.data.network.dto.BriefResponseDto
import com.daragent.data.network.dto.BriefUpdateRequest
import com.daragent.data.network.dto.GenerationResponse
import com.daragent.data.network.dto.ProjectCreateRequest
import com.daragent.data.network.dto.ProjectResponseDto
import com.daragent.data.network.dto.RecommendationResponseDto
import com.daragent.data.network.dto.RecommendationSelectRequest
import com.daragent.data.network.dto.StartGenerationRequest
import com.daragent.domain.model.Brief
import com.daragent.domain.model.Occasion
import com.daragent.domain.model.Project
import com.daragent.domain.model.Recommendation
import com.daragent.domain.repository.ProjectRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class ProjectRepositoryImpl(
    private val projectsApi: ProjectsApi,
    private val briefsApi: BriefsApi,
    private val recommendationsApi: RecommendationsApi,
    private val holidaysApi: HolidaysApi,
    private val generationsApi: GenerationsApi
) : ProjectRepository {
    override suspend fun create(recipientId: String, occasionCode: String, occasionTitle: String?, title: String?): Result<Project> =
        withContext(Dispatchers.IO) {
            runCatching {
                val response = projectsApi.create(ProjectCreateRequest(recipientId, occasionCode, occasionTitle, title)).body()!!
                response.toDomain()
            }
        }

    override suspend fun getBrief(projectId: String): Result<Brief> =
        withContext(Dispatchers.IO) {
            runCatching {
                briefsApi.get(projectId).body()!!.toDomain()
            }
        }

    override suspend fun updateBrief(projectId: String, brief: Brief): Result<Brief> =
        withContext(Dispatchers.IO) {
            runCatching {
                briefsApi.update(projectId, BriefUpdateRequest(
                    occasion_text = brief.occasionText,
                    sender_role = brief.senderRole,
                    recipient_role = brief.recipientRole,
                    relationship = brief.relationship,
                    relationship_text = null,
                    desired_mood = brief.desiredMood,
                    humor_level = brief.humorLevel,
                    emotion_level = brief.emotionLevel,
                    surprise_level = brief.surpriseLevel,
                    inside_joke = brief.insideJoke,
                    hobbies_text = brief.hobbiesText,
                    character_traits = brief.characterTraits,
                    memorable_story = brief.memorableStory,
                    desired_phrase = brief.desiredPhrase,
                    forbidden_topics = brief.forbiddenTopics,
                    sender_message = brief.senderMessage
                )).body()!!.toDomain()
            }
        }

    override suspend fun completeBrief(projectId: String): Result<Brief> =
        withContext(Dispatchers.IO) {
            runCatching {
                briefsApi.complete(projectId).body()!!.toDomain()
            }
        }

    override suspend fun getRecommendations(projectId: String): Result<List<Recommendation>> =
        withContext(Dispatchers.IO) {
            runCatching {
                recommendationsApi.list(projectId).body().orEmpty().map { it.toDomain() }
            }
        }

    override suspend fun selectRecommendation(projectId: String, recommendationId: String): Result<Recommendation> =
        withContext(Dispatchers.IO) {
            runCatching {
                recommendationsApi.select(projectId, RecommendationSelectRequest(recommendationId)).body()!!.toDomain()
            }
        }

    override suspend fun startGeneration(projectId: String, templateVersionId: String): Result<com.daragent.domain.model.Generation> =
        withContext(Dispatchers.IO) {
            runCatching {
                generationsApi.start(StartGenerationRequest(projectId, templateVersionId)).body()!!.toDomain()
            }
        }

    override suspend fun listOccasions(): Result<List<Occasion>> =
        withContext(Dispatchers.IO) {
            runCatching {
                holidaysApi.list().body().orEmpty().map { it.toDomain() }
            }
        }
}

private fun ProjectResponseDto.toDomain() = Project(
    id = id,
    recipientId = recipient_id,
    title = title,
    status = status,
    occasionCode = occasion_code,
    occasionTitle = occasion_title,
    priceRub = price_rub,
    selectedTemplateVersionId = selected_template_version_id
)

private fun BriefResponseDto.toDomain() = Brief(
    id = id,
    projectId = project_id,
    status = status,
    occasionText = occasion_text,
    senderRole = sender_role,
    recipientRole = recipient_role,
    relationship = relationship,
    desiredMood = desired_mood,
    humorLevel = humor_level,
    emotionLevel = emotion_level,
    surpriseLevel = surprise_level,
    insideJoke = inside_joke,
    hobbiesText = hobbies_text,
    characterTraits = character_traits,
    memorableStory = memorable_story,
    desiredPhrase = desired_phrase,
    forbiddenTopics = forbidden_topics,
    senderMessage = sender_message
)

private fun RecommendationResponseDto.toDomain() = Recommendation(
    id = id,
    projectId = project_id,
    templateVersionId = template_version_id,
    rank = rank,
    score = score,
    matchReasons = match_reasons,
    explanation = explanation,
    selectedAt = selected_at
)

private fun GenerationResponse.toDomain() = com.daragent.domain.model.Generation(
    id = id,
    projectId = project_id,
    status = status,
    progress = progress,
    currentStep = current_step,
    estimatedSeconds = estimated_seconds
)
