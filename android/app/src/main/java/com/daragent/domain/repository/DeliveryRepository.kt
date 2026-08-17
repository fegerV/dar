package com.daragent.domain.repository

import com.daragent.domain.model.Delivery

interface DeliveryRepository {
    suspend fun getByProject(projectId: String): Result<Delivery>
}
