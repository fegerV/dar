package com.daragent.data.network.stream

import okhttp3.Call
import okhttp3.Callback
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okio.buffer
import okio.source
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit

object SseClient {
    private const val CONNECT_TIMEOUT_SECONDS = 10L
    private const val READ_TIMEOUT_SECONDS = 300L

    fun streamGenerationProgress(
        baseUrl: String,
        generationId: String,
        accessToken: String,
        onEvent: (SseEvent) -> Unit,
        onError: (Throwable) -> Unit,
        onComplete: () -> Unit
    ): Call {
        val client = OkHttpClient.Builder()
            .connectTimeout(CONNECT_TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .readTimeout(READ_TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .build()

        val url = "$baseUrl/generations/$generationId/stream"
        val request = Request.Builder()
            .url(url)
            .addHeader("Authorization", "Bearer $accessToken")
            .addHeader("Accept", "text/event-stream")
            .build()

        val call = client.newCall(request)
        call.enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                onError(e)
            }

            override fun onResponse(call: Call, response: Response) {
                val body = response.body ?: run {
                    onError(IOException("Empty SSE body"))
                    return
                }
                val source = body.source().buffer()
                try {
                    while (!source.exhausted()) {
                        val line = source.readUtf8LineStrict() ?: continue
                        if (line.startsWith("data:")) {
                            val payload = line.removePrefix("data:").trim()
                            val json = JSONObject(payload)
                            val event = SseEvent(
                                generationId = json.optString("generation_id"),
                                status = json.optString("status"),
                                progress = json.optInt("progress", 0),
                                currentStep = json.optString("current_step", null),
                                estimatedSeconds = if (json.has("estimated_seconds") && !json.isNull("estimated_seconds")) json.optInt("estimated_seconds") else null,
                                timestamp = json.optString("timestamp", null)
                            )
                            onEvent(event)
                            if (event.status in setOf("completed", "failed", "cancelled", "approved", "rejected")) {
                                break
                            }
                        }
                    }
                    onComplete()
                } catch (e: Exception) {
                    onError(e)
                }
            }
        })
        return call
    }

    data class SseEvent(
        val generationId: String,
        val status: String,
        val progress: Int,
        val currentStep: String?,
        val estimatedSeconds: Int?,
        val timestamp: String?
    )
}
