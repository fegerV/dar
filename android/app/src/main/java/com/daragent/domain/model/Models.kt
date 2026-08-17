package com.daragent.domain.model

data class Person(
    val id: String,
    val name: String,
    val relationship: String,
    val birthDate: String?,
    val interests: List<String>,
    val insideJokes: List<String>
)

data class Template(
    val id: String,
    val title: String,
    val category: String,
    val previewUrl: String?,
    val priceRub: Double
)

data class Generation(
    val id: String,
    val projectId: String,
    val status: String,
    val progress: Int,
    val currentStep: String?,
    val estimatedSeconds: Int?
)
