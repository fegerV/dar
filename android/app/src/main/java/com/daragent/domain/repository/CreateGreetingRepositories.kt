package com.daragent.domain.repository

import com.daragent.domain.model.Brief
import com.daragent.domain.model.Occasion
import com.daragent.domain.model.Project
import com.daragent.domain.model.Recommendation

interface ProjectRepository {
    suspend fun create(recipientId: String, occasionCode: String, occasionTitle: String?, title: String?): Result<Project>
    suspend fun getBrief(projectId: String): Result<Brief>
    suspend fun updateBrief(projectId: String, brief: Brief): Result<Brief>
    suspend fun completeBrief(projectId: String): Result<Brief>
    suspend fun getRecommendations(projectId: String): Result<List<Recommendation>>
    suspend fun selectRecommendation(projectId: String, recommendationId: String): Result<Recommendation>
    suspend fun listOccasions(): Result<List<Occasion>>
}
