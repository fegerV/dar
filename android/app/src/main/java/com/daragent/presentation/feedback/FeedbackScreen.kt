package com.daragent.presentation.feedback

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
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
fun FeedbackScreen(
    projectId: String,
    modifier: Modifier = Modifier,
    onBack: () -> Unit = {},
) {
    val mascotRepository = remember { MascotRepository() }
    val viewModel: FeedbackViewModel = viewModel(
        factory = FeedbackViewModelFactory(ServiceLocator.feedbackRepository)
    )
    val state by viewModel.state.collectAsState()

    LaunchedEffect(Unit) {
        mascotRepository.handleEvent(MascotEvent.ANSWER_RECEIVED, "Оцените ваше поздравление!")
        viewModel.loadStats(projectId)
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
            text = "Как вам поздравление?",
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFF37306B),
            modifier = Modifier.padding(bottom = 24.dp),
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceEvenly,
        ) {
            val reactions = listOf(
                "🔥" to "fire",
                "❤️" to "heart",
                "😂" to "laugh",
                "😭" to "cry",
                "😐" to "neutral",
            )

            reactions.forEach { (emoji, code) ->
                Button(
                    onClick = {
                        viewModel.addReaction(projectId, code)
                        mascotRepository.handleEvent(MascotEvent.SHARE_COMPLETED, "Спасибо за оценку!")
                    },
                    modifier = Modifier
                        .size(56.dp)
                        .padding(4.dp),
                    shape = RoundedCornerShape(12.dp),
                ) {
                    Text(emoji, fontSize = 24.sp)
                }
            }
        }

        state.stats?.let { stats ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 16.dp),
                shape = RoundedCornerShape(12.dp),
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        "Всего реакций: ${stats.totalReactions}",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    stats.averageRating?.let {
                        Text("Средний рейтинг: $it", style = MaterialTheme.typography.bodyMedium)
                    }
                    Text(
                        "Негативных: ${stats.negativeCount}",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color.Red,
                    )
                }
            }
        }

        Button(onClick = onBack, modifier = Modifier.padding(top = 16.dp)) {
            Text("Назад")
        }
    }
}

class FeedbackViewModelFactory(
    private val repo: com.daragent.domain.repository.FeedbackRepository,
) : androidx.lifecycle.ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : androidx.lifecycle.ViewModel> create(modelClass: Class<T>): T {
        return FeedbackViewModel(repo) as T
    }
}
