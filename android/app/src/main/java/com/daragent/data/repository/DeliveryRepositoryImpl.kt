package com.daragent.data.repository

import com.daragent.data.network.api.DeliveriesApi
import com.daragent.data.network.dto.DeliveryListResponse
import com.daragent.domain.model.Delivery
import com.daragent.domain.repository.DeliveryRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class DeliveryRepositoryImpl(private val api: DeliveriesApi) : DeliveryRepository {
    override suspend fun getByProject(projectId: String): Result<List<Delivery>> =
        withContext(Dispatchers.IO) {
            runCatching { api.byProject(projectId).body()!!.items.map { it.toDomain() } }
        }
}

private fun com.daragent.data.network.dto.DeliveryResponseDto.toDomain() = Delivery(
    id = id,
    projectId = project_id,
    channel = channel,
    status = status,
    destination = destination,
    publicUrl = public_url,
    createdAt = created_at,
    scheduledAt = scheduled_at,
    sentAt = sent_at,
    openedAt = opened_at
)
