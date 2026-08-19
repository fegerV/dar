package com.daragent.presentation.referral

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.daragent.di.ServiceLocator
import com.daragent.presentation.mascot.MascotEvent
import com.daragent.presentation.mascot.MascotRepository
import com.daragent.presentation.mascot.MascotView

@Composable
fun ReferralScreen(
    modifier: Modifier = Modifier,
    onBack: () -> Unit = {},
) {
    val mascotRepository = remember { MascotRepository() }
    val viewModel: ReferralViewModel = viewModel(
        factory = ReferralViewModelFactory(ServiceLocator.referralRepository)
    )
    val state by viewModel.state.collectAsState()

    LaunchedEffect(Unit) {
        mascotRepository.handleEvent(
            MascotEvent.REFERRAL_COMPLETED,
            state.stats?.let { "Ты пригнал ${it.completedReferrals} другов! Возвращается ${it.earnedRub} ₽." }
                ?: "Приглашай друзей и получай бонусы!"
        )
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(Color(0xFFF8FAFC))
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        MascotView(
            modifier = Modifier
                .size(160.dp)
                .padding(bottom = 16.dp),
        )

        Text(
            text = "Реферальная программа",
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFF37306B),
            modifier = Modifier.padding(bottom = 16.dp),
        )

        state.error?.let {
            Text(text = it, color = Color.Red, modifier = Modifier.padding(8.dp))
        }

        state.stats?.let { stats ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(8.dp),
                shape = RoundedCornerShape(12.dp),
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Всего рефералов: ${stats.totalReferrals}", style = MaterialTheme.typography.bodyMedium)
                    Text("Выполнено: ${stats.completedReferrals}", style = MaterialTheme.typography.bodyMedium)
                    Text("Заработано: ${stats.earnedRub} ₽", style = MaterialTheme.typography.bodyMedium)
                    Text("Бонус приглашения: ${stats.referrerBonusRub} ₽", style = MaterialTheme.typography.bodySmall)
                    Text("Бонус друга: ${stats.refereeBonusRub} ₽", style = MaterialTheme.typography.bodySmall)
                }
            }
        }

        state.code?.let { code ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(8.dp),
                shape = RoundedCornerShape(12.dp),
            ) {
                Column(modifier = Modifier.padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("Твой код:", style = MaterialTheme.typography.bodySmall)
                    Text(code.code, fontSize = 24.sp, fontWeight = FontWeight.Bold, color = Color(0xFF37306B))
                    Text("Использовано: ${code.uses}", style = MaterialTheme.typography.bodySmall)
                }
            }
        }

        var applyCode by remember { mutableStateOf("") }
        TextField(
            value = applyCode,
            onValueChange = { applyCode = it },
            label = { Text("Введите реферальный код") },
            singleLine = true,
            modifier = Modifier
                .fillMaxWidth()
                .padding(8.dp),
        )

        Button(
            onClick = { viewModel.applyCode(applyCode) },
            modifier = Modifier
                .fillMaxWidth()
                .padding(8.dp),
            enabled = applyCode.isNotBlank() && !state.isLoading,
        ) {
            Text(if (state.isLoading) "Применяю..." else "Применить код")
        }

        Button(onClick = onBack, modifier = Modifier.padding(8.dp)) {
            Text("Назад")
        }
    }
}

class ReferralViewModelFactory(
    private val repo: com.daragent.domain.repository.ReferralRepository,
) : androidx.lifecycle.ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : androidx.lifecycle.ViewModel> create(modelClass: Class<T>): T {
        return ReferralViewModel(repo) as T
    }
}
