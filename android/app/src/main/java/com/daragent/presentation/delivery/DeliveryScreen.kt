package com.daragent.presentation.delivery

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
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel

@Composable
fun DeliveryScreen(
    projectId: String,
    viewModel: DeliveryViewModel = viewModel(),
    onBack: () -> Unit = {}
) {
    val state by viewModel.state.collectAsState()
    Column(modifier = Modifier.fillMaxSize(), horizontalAlignment = Alignment.CenterHorizontally) {
        Text(text = "Доставка поздравления", modifier = Modifier.padding(16.dp))
        Text(text = "Статус доставки: ${state.status}", modifier = Modifier.padding(16.dp))
        LinearProgressIndicator(progress = state.progress / 100f, modifier = Modifier.fillMaxWidth().padding(16.dp))
        state.publicUrl?.let { Text(text = "Ссылка: $it", modifier = Modifier.padding(16.dp)) }
        state.error?.let { Text(text = it, modifier = Modifier.padding(16.dp)) }
        Button(onClick = onBack, modifier = Modifier.padding(16.dp)) {
            Text("Назад")
        }
    }

    LaunchedEffect(projectId) {
        viewModel.startTracking(projectId)
    }
}
