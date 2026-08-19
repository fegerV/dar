package com.daragent.presentation.home

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
import androidx.navigation.NavHostController

@Composable
fun HomeScreen(
    navController: NavHostController? = null,
    onNewGreeting: () -> Unit = {},
    viewModel: HomeViewModel = viewModel()
) {
    val state by viewModel.state.collectAsState()
    Column(modifier = Modifier.fillMaxSize(), horizontalAlignment = Alignment.CenterHorizontally) {
        Text(text = state.user?.displayName?.let { "Привет, $it!" } ?: "Кого будем удивлять?", modifier = Modifier.padding(16.dp))
        if (state.isLoading) {
            Text(text = "Загрузка...", modifier = Modifier.padding(16.dp))
        }
        state.error?.let { Text(text = it, modifier = Modifier.padding(16.dp)) }
        if (state.people.isNotEmpty()) {
            Text(text = "Ваши люди", modifier = Modifier.padding(start = 16.dp, end = 16.dp, top = 8.dp))
            LazyColumn(modifier = Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                items(state.people) { person ->
                    Card(modifier = Modifier.padding(horizontal = 16.dp)) {
                        Text(text = person.name, modifier = Modifier.padding(16.dp))
                    }
                }
            }
        }
        Button(onClick = onNewGreeting, modifier = Modifier.padding(16.dp)) {
            Text("+ Новое поздравление")
        }
        Button(
            onClick = { navController?.navigate("referral") },
            modifier = Modifier.padding(16.dp),
        ) {
            Text("Реферальная программа")
        }
        Button(
            onClick = { navController?.navigate("settings") },
            modifier = Modifier.padding(16.dp),
        ) {
            Text("Настройки")
        }
    }
}
