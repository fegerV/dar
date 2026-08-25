package com.daragent.core.network.model.chat

import com.squareup.moshi.Json
import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class ChatMessageRequest(
    @Json(name = "text") val text: String,
    @Json(name = "project_id") val projectId: String? = null,
)

@JsonClass(generateAdapter = true)
data class ChatAction(
    @Json(name = "type") val type: String,
    @Json(name = "label") val label: String,
    @Json(name = "payload") val payload: Map<String, Any> = emptyMap(),
)

@JsonClass(generateAdapter = true)
data class ChatMessageResponse(
    @Json(name = "id") val id: String,
    @Json(name = "project_id") val projectId: String,
    @Json(name = "text") val text: String,
    @Json(name = "sender") val sender: String,
    @Json(name = "suggestions") val suggestions: List<String> = emptyList(),
    @Json(name = "actions") val actions: List<ChatAction> = emptyList(),
    @Json(name = "created_at") val createdAt: String,
)

@JsonClass(generateAdapter = true)
data class ProjectCreateRequest(
    @Json(name = "recipient_name") val recipientName: String? = null,
    @Json(name = "recipient_id") val recipientId: String? = null,
    @Json(name = "occasion") val occasion: String? = null,
    @Json(name = "mood") val mood: String? = null,
)

@JsonClass(generateAdapter = true)
data class ProjectResponse(
    @Json(name = "id") val id: String,
    @Json(name = "status") val status: String,
    @Json(name = "recipient_name") val recipientName: String? = null,
    @Json(name = "occasion") val occasion: String? = null,
    @Json(name = "mood") val mood: String? = null,
    @Json(name = "concept") val concept: String? = null,
    @Json(name = "text") val text: String? = null,
    @Json(name = "created_at") val createdAt: String,
)
