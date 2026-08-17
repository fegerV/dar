package com.daragent.domain.model

data class Delivery(
    val id: String,
    val projectId: String,
    val channel: String,
    val status: String,
    val destination: String?,
    val publicUrl: String?,
    val createdAt: String,
    val scheduledAt: String?,
    val sentAt: String?,
    val openedAt: String?
)
