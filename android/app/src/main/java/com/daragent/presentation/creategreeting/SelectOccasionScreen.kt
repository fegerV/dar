package com.daragent.presentation.creategreeting

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel

@Composable
fun SelectOccasionScreen(
    viewModel: CreateGreetingViewModel = viewModel(),
    onNext: () -> Unit = {},
    onBack: () -> Unit = {}
) {
    val state by viewModel.state.collectAsState()
    Column(modifier = Modifier.fillMaxSize(), horizontalAlignment = Alignment.CenterHorizontally) {
        Text(text = "Выберите повод", modifier = Modifier.padding(16.dp))
        if (state.isLoading) {
            Text(text = "Загрузка...", modifier = Modifier.padding(16.dp))
        }
        state.error?.let { Text(text = it, modifier = Modifier.padding(16.dp)) }
        LazyColumn(modifier = Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(state.occasions) { occasion ->
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp)
                        .clickable {
                            viewModel.selectOccasion(occasion)
                            onNext()
                        }
                ) {
                    Text(text = occasion.title, modifier = Modifier.padding(16.dp))
                }
            }
        }
        Button(onClick = onBack, modifier = Modifier.padding(16.dp)) {
            Text("Назад")
        }
    }
}
