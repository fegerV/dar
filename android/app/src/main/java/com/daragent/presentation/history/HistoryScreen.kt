package com.daragent.presentation.history

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel

@Composable
fun HistoryScreen(
    onProjectClick: (String) -> Unit = {},
    onBack: () -> Unit = {}
) {
    val viewModel: HistoryViewModel = viewModel()
    val state by viewModel.state.collectAsState()

    Column(modifier = Modifier.fillMaxSize()) {
        if (state.isLoading) {
            Text(text = "Загрузка...", modifier = Modifier.padding(16.dp))
        }
        state.error?.let { Text(text = it, modifier = Modifier.padding(16.dp)) }

        if (state.projects.isEmpty() && !state.isLoading) {
            Column(
                modifier = Modifier.fillMaxSize(),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Text(text = "История поздравлений пуста", modifier = Modifier.padding(16.dp))
            }
        }

        LazyColumn(modifier = Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(state.projects) { project ->
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp)
                        .clickable { onProjectClick(project.id) }
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(text = project.title ?: "Без названия", fontWeight = FontWeight.Bold)
                        Text(text = "Статус: ${project.status}", modifier = Modifier.padding(top = 4.dp))
                        Text(text = "%.0f ₽".format(project.priceRub), modifier = Modifier.padding(top = 4.dp))
                    }
                }
            }
        }
    }
}
