package com.daragent.data.network.api

import com.daragent.data.network.NetworkModule
import com.daragent.data.network.dto.DeliveryListResponse
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Path

interface DeliveriesApi {
    @GET("delivery/projects/{project_id}")
    suspend fun byProject(@Path("project_id") projectId: String): Response<DeliveryListResponse>
}
