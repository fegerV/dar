package com.daragent.presentation.creategreeting

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel

@Composable
fun GenerationScreen(
    viewModel: CreateGreetingViewModel = viewModel(),
    onBack: () -> Unit = {}
) {
    val state by viewModel.state.collectAsState()
    Column(modifier = Modifier.fillMaxSize(), horizontalAlignment = Alignment.CenterHorizontally) {
        Text(text = "Генерация поздравления", modifier = Modifier.padding(16.dp))
        state.generation?.let { gen ->
            Text(text = "Статус: ${gen.status}", modifier = Modifier.padding(16.dp))
            LinearProgressIndicator(progress = gen.progress / 100f, modifier = Modifier.fillMaxWidth().padding(16.dp))
            Text(text = "Шаг: ${gen.currentStep ?: "..."}", modifier = Modifier.padding(horizontal = 16.dp))
            gen.estimatedSeconds?.let { Text(text = "Примерное время: $it сек", modifier = Modifier.padding(16.dp)) }
        }
        state.error?.let { Text(text = it, modifier = Modifier.padding(16.dp)) }
        Button(onClick = onBack, modifier = Modifier.padding(16.dp)) {
            Text("Назад")
        }
    }
}
