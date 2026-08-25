package com.daragent.core.network.api

import com.daragent.core.network.model.chat.ChatMessageRequest
import com.daragent.core.network.model.chat.ChatMessageResponse
import com.daragent.core.network.model.chat.ProjectCreateRequest
import com.daragent.core.network.model.chat.ProjectResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface ChatApi {
    @POST("/api/v1/chat/message")
    suspend fun sendMessage(@Body request: ChatMessageRequest): Response<ChatMessageResponse>

    @POST("/api/v1/chat/projects")
    suspend fun createProject(@Body request: ProjectCreateRequest): Response<ProjectResponse>

    @GET("/api/v1/chat/projects/{projectId}")
    suspend fun getProject(@Path("projectId") projectId: String): Response<ProjectResponse>
}
