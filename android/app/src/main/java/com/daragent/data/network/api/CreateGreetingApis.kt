package com.daragent.data.network.api

import com.daragent.data.network.dto.BriefResponseDto
import com.daragent.data.network.dto.BriefUpdateRequest
import com.daragent.data.network.dto.ProjectCreateRequest
import com.daragent.data.network.dto.ProjectResponseDto
import com.daragent.data.network.dto.RecommendationResponseDto
import com.daragent.data.network.dto.RecommendationSelectRequest
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PATCH
import retrofit2.http.Path
import retrofit2.http.Query

interface ProjectsApi {
    @POST("projects")
    suspend fun create(@Body request: ProjectCreateRequest): Response<ProjectResponseDto>

    @GET("projects")
    suspend fun list(): Response<List<ProjectResponseDto>>
}

interface BriefsApi {
    @PATCH("projects/{project_id}/brief")
    suspend fun update(@Path("project_id") projectId: String, @Body request: BriefUpdateRequest): Response<BriefResponseDto>

    @GET("projects/{project_id}/brief")
    suspend fun get(@Path("project_id") projectId: String): Response<BriefResponseDto>

    @POST("projects/{project_id}/brief/complete")
    suspend fun complete(@Path("project_id") projectId: String): Response<BriefResponseDto>
}

interface RecommendationsApi {
    @GET("projects/{project_id}/recommendations")
    suspend fun list(@Path("project_id") projectId: String): Response<List<RecommendationResponseDto>>

    @POST("projects/{project_id}/recommendations/select")
    suspend fun select(@Path("project_id") projectId: String, @Body request: RecommendationSelectRequest): Response<RecommendationResponseDto>
}
