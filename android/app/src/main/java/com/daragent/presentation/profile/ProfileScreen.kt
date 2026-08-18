package com.daragent.presentation.profile

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
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
fun ProfileScreen(
    onBack: () -> Unit = {},
    onLogin: () -> Unit = {}
) {
    val viewModel: ProfileViewModel = viewModel()
    val state by viewModel.state.collectAsState()

    if (state.user == null && !state.isLoading) {
        Column(
            modifier = Modifier.fillMaxSize(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(text = "Необходимо войти", modifier = Modifier.padding(16.dp))
            Button(onClick = onLogin) { Text("Войти") }
        }
        return
    }

    Column(modifier = Modifier.fillMaxSize()) {
        Card(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = state.user?.displayName ?: "Пользователь",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
                Text(text = state.user?.email ?: "", modifier = Modifier.padding(top = 4.dp))
                Text(text = "ID: ${state.user?.id}", modifier = Modifier.padding(top = 4.dp))
            }
        }

        state.wallet?.let { wallet ->
            Card(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp)) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(text = "Баланс", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    Text(text = "%.0f ₽".format(wallet.balanceRub), modifier = Modifier.padding(top = 8.dp))
                    Text(text = "Бонусы: %.0f".format(wallet.bonusBalance), modifier = Modifier.padding(top = 4.dp))
                }
            }
        }

        Card(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(text = "Доступные генерации", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                if (state.entitlements.isEmpty()) {
                    Text(text = "Нет бесплатных генераций", modifier = Modifier.padding(top = 8.dp))
                } else {
                    LazyColumn(modifier = Modifier.fillMaxWidth()) {
                        items(state.entitlements) { entitlement ->
                            Row(
                                modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Column {
                                    Text(text = entitlement.code, fontWeight = FontWeight.Bold)
                                    Text(text = "Осталось: ${entitlement.quantity - entitlement.consumed}")
                                }
                                entitlement.expiresAt?.let {
                                    Text(text = " до ${it.take(10)}")
                                }
                            }
                        }
                    }
                }
            }
        }

        Button(onClick = { viewModel.logout() }, modifier = Modifier.padding(16.dp)) {
            Text("Выйти")
        }
    }
}
