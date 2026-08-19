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
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.daragent.presentation.mascot.MascotEvent
import com.daragent.presentation.mascot.MascotRepository
import com.daragent.presentation.mascot.MascotView

@Composable
fun GenerationScreen(
    viewModel: CreateGreetingViewModel = viewModel(),
    onBack: () -> Unit = {}
) {
    val state by viewModel.state.collectAsState()
    val mascotRepository = remember { MascotRepository() }

    LaunchedEffect(state.generation?.status) {
        val gen = state.generation
        when (gen?.status) {
            "processing", "queued" -> {
                mascotRepository.handleEvent(MascotEvent.GENERATION_STARTED, "Генерирую ваше поздравление...")
            }
            "completed" -> {
                mascotRepository.handleEvent(MascotEvent.GENERATION_COMPLETED, "Готово! 🎉")
            }
            "failed" -> {
                mascotRepository.handleEvent(MascotEvent.GENERATION_FAILED)
            }
        }
    }

    Column(modifier = Modifier.fillMaxSize()) {
        MascotView(
            modifier = Modifier
                .fillMaxWidth()
                .height(200.dp),
        )
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(text = "Генерация поздравления", modifier = Modifier.padding(16.dp))
            state.generation?.let { gen ->
                Text(text = "Статус: ${gen.status}", modifier = Modifier.padding(16.dp))
                LinearProgressIndicator(
                    progress = gen.progress / 100f,
                    modifier = Modifier.fillMaxWidth().padding(16.dp),
                )
                Text(text = "Шаг: ${gen.currentStep ?: "..."}", modifier = Modifier.padding(horizontal = 16.dp))
                gen.estimatedSeconds?.let { Text(text = "Примерное время: $it сек", modifier = Modifier.padding(16.dp)) }
            }
            state.error?.let { Text(text = it, modifier = Modifier.padding(16.dp)) }
            Button(onClick = onBack, modifier = Modifier.padding(16.dp)) {
                Text("Назад")
            }
        }
    }
}
