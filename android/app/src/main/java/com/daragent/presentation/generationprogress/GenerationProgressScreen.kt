package com.daragent.presentation.generationprogress

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import com.daragent.presentation.creategreeting.GenerationScreen

@Composable
fun GenerationProgressScreen(
    generationId: String,
    accessToken: String,
    navController: NavHostController? = null,
    viewModel: GenerationProgressViewModel = viewModel(),
    onBack: () -> Unit = {}
) {
    val state by viewModel.state.collectAsState()
    Column(modifier = Modifier.fillMaxSize(), horizontalAlignment = Alignment.CenterHorizontally) {
        Text(text = "Генерация в процессе...", modifier = Modifier.padding(16.dp))
        state.generation?.let { gen ->
            Text(text = "Статус: ${gen.status}", modifier = Modifier.padding(16.dp))
            LinearProgressIndicator(
                progress = gen.progress / 100f,
                modifier = Modifier.fillMaxWidth().padding(16.dp)
            )
            Text(text = "Прогресс: ${gen.progress}%", modifier = Modifier.padding(horizontal = 16.dp))
            gen.currentStep?.let { Text(text = "Шаг: $it", modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp)) }
            gen.estimatedSeconds?.let { Text(text = "Осталось примерно: $it сек", modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp)) }
        }
        if (state.steps.isNotEmpty()) {
            Text(text = "Этапы:", modifier = Modifier.padding(start = 16.dp, end = 16.dp, top = 16.dp))
            LazyColumn(modifier = Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                items(state.steps) { step ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(
                                if (step.status == "completed") MaterialTheme.colorScheme.primaryContainer
                                else MaterialTheme.colorScheme.surface
                            )
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(text = "${step.stepNo}. ${step.stepCode}")
                        Text(text = step.status)
                    }
                }
            }
        }
        state.error?.let { Text(text = it, modifier = Modifier.padding(16.dp)) }
        Button(onClick = onBack, modifier = Modifier.padding(16.dp)) {
            Text("Назад")
        }
    }

    LaunchedEffect(Unit) {
        viewModel.startStreaming(generationId)
    }
}
