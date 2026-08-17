package com.daragent.presentation.payment

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
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel

@Composable
fun PaymentScreen(
    projectId: String,
    amount: Double,
    viewModel: PaymentViewModel = viewModel(),
    onBack: () -> Unit = {},
    onSuccess: () -> Unit = {}
) {
    val state by viewModel.state.collectAsState()

    LaunchedEffect(projectId, amount) {
        viewModel.init(projectId, amount)
    }

    Column(modifier = Modifier.fillMaxSize(), horizontalAlignment = Alignment.CenterHorizontally) {
        Text(text = "Оплата", modifier = Modifier.padding(16.dp))
        Text(text = "Сумма: %.2f ₽".format(state.amount), modifier = Modifier.padding(horizontal = 16.dp))
        state.wallet?.let { wallet ->
            Text(text = "Баланс: %.2f ₽".format(wallet.balanceRub), modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp))
            Text(text = "Бонусы: %.2f".format(wallet.bonusBalance), modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp))
        }
        if (state.entitlements.isNotEmpty()) {
            Text(text = "Доступно бесплатных генераций:", modifier = Modifier.padding(start = 16.dp, end = 16.dp, top = 16.dp))
            LazyColumn(modifier = Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                items(state.entitlements) { entitlement ->
                    Card(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp)) {
                        Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                            RadioButton(
                                selected = state.selectedMethod == "entitlement:${entitlement.id}",
                                onClick = {
                                    viewModel.selectMethod("entitlement:${entitlement.id}")
                                    viewModel.useEntitlement(entitlement.id)
                                }
                            )
                            Column(modifier = Modifier.padding(start = 8.dp)) {
                                Text(text = entitlement.code)
                                Text(text = "Осталось: ${entitlement.quantity - entitlement.consumed}")
                            }
                        }
                    }
                }
            }
        }
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            PaymentMethod.values().forEach { method ->
                Card(
                    modifier = Modifier
                        .weight(1f)
                        .padding(horizontal = 8.dp)
                        .padding(top = 16.dp)
                ) {
                    Column(modifier = Modifier.padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        RadioButton(
                            selected = state.selectedMethod == method.name.lowercase(),
                            onClick = { viewModel.selectMethod(method.name.lowercase()) }
                        )
                        Text(text = method.title)
                    }
                }
            }
        }
        if (state.error != null) {
            Text(text = state.error, modifier = Modifier.padding(16.dp))
        }
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = onBack, modifier = Modifier.weight(1f).padding(16.dp)) {
                Text("Назад")
            }
            Button(onClick = {
                viewModel.pay()
                onSuccess()
            }, modifier = Modifier.weight(1f).padding(16.dp), enabled = !state.isLoading) {
                Text("Оплатить")
            }
        }
    }
}

enum class PaymentMethod(val title: String) {
    CARD("Карта"),
    WALLET("Кошелёк"),
    BONUS("Бонусы"),
    PROMO("Промокод")
}
