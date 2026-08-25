package com.daragent.presentation.generation

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Error
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel

@Composable
fun GenerationScreen(
    onBack: () -> Unit,
    onNavigateToResult: () -> Unit,
    viewModel: GenerationViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(uiState.status) {
        if (uiState.status == GenerationStatus.COMPLETED) {
            kotlinx.coroutines.delay(500)
            onNavigateToResult()
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        MaterialTheme.colorScheme.background,
                        MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f),
                    )
                )
            ),
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
        ) {
            MascotAnimation(
                isAnimating = uiState.status == GenerationStatus.PROCESSING,
            )

            Spacer(modifier = Modifier.height(32.dp))

            when (uiState.status) {
                GenerationStatus.IDLE -> IdleState(onStartClick = { viewModel.startGeneration() })
                GenerationStatus.QUEUED -> QueuedState()
                GenerationStatus.PROCESSING -> ProcessingState(
                    progress = uiState.progress,
                    message = uiState.statusMessage,
                    onCancelClick = { viewModel.cancelGeneration() },
                )
                GenerationStatus.COMPLETED -> CompletedState()
                GenerationStatus.FAILED -> FailedState(
                    errorMessage = uiState.errorMessage ?: "Произошла ошибка",
                    onRetryClick = { viewModel.startGeneration() },
                )
                GenerationStatus.CANCELLED -> CancelledState(
                    onStartClick = { viewModel.startGeneration() },
                )
            }
        }
    }
}

@Composable
private fun MascotAnimation(isAnimating: Boolean) {
    val infiniteTransition = rememberInfiniteTransition(label = "mascot")
    val scale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 1.2f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = EaseInOutSine),
            repeatMode = RepeatMode.Reverse,
        ),
        label = "scale",
    )
    val rotation by infiniteTransition.animateFloat(
        initialValue = -5f,
        targetValue = 5f,
        animationSpec = infiniteRepeatable(
            animation = tween(1500, easing = EaseInOutSine),
            repeatMode = RepeatMode.Reverse,
        ),
        label = "rotation",
    )

    Box(
        modifier = Modifier
            .size(120.dp)
            .clip(CircleShape)
            .background(MaterialTheme.colorScheme.primaryContainer),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = "🦊",
            style = MaterialTheme.typography.displayLarge,
            modifier = if (isAnimating) {
                Modifier
                    .scale(scale)
                    .graphicsLayer { rotationZ = rotation }
            } else {
                Modifier
            },
        )
    }
}

@Composable
private fun IdleState(onStartClick: () -> Unit) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = "Готовы начать?",
            style = MaterialTheme.typography.headlineSmall,
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = "Дарагент создаст уникальное поздравление",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center,
        )
        Spacer(modifier = Modifier.height(24.dp))
        Button(
            onClick = onStartClick,
            modifier = Modifier.testTag("btn_start_generation"),
        ) {
            Text("🎬 Создать поздравление")
        }
    }
}

@Composable
private fun QueuedState() {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        CircularProgressIndicator()
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "В очереди...",
            style = MaterialTheme.typography.titleMedium,
        )
    }
}

@Composable
private fun ProcessingState(
    progress: Int,
    message: String,
    onCancelClick: () -> Unit,
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier.testTag("generation_processing"),
    ) {
        Box(
            contentAlignment = Alignment.Center,
        ) {
            CircularProgressIndicator(
                progress = { progress / 100f },
                modifier = Modifier.size(120.dp),
                strokeWidth = 8.dp,
            )
            Text(
                text = "$progress%",
                style = MaterialTheme.typography.titleLarge,
            )
        }
        Spacer(modifier = Modifier.height(24.dp))
        Text(
            text = message,
            style = MaterialTheme.typography.titleMedium,
            textAlign = TextAlign.Center,
        )
        Spacer(modifier = Modifier.height(24.dp))
        OutlinedButton(
            onClick = onCancelClick,
            modifier = Modifier.testTag("btn_cancel"),
        ) {
            Text("Отменить")
        }
    }
}

@Composable
private fun CompletedState() {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Icon(
            Icons.Default.CheckCircle,
            contentDescription = null,
            modifier = Modifier.size(64.dp),
            tint = MaterialTheme.colorScheme.primary,
        )
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "Готово!",
            style = MaterialTheme.typography.headlineSmall,
            color = MaterialTheme.colorScheme.primary,
        )
    }
}

@Composable
private fun FailedState(
    errorMessage: String,
    onRetryClick: () -> Unit,
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier.testTag("generation_failed"),
    ) {
        Icon(
            Icons.Default.Error,
            contentDescription = null,
            modifier = Modifier.size(64.dp),
            tint = MaterialTheme.colorScheme.error,
        )
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "Ошибка",
            style = MaterialTheme.typography.headlineSmall,
            color = MaterialTheme.colorScheme.error,
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = errorMessage,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center,
        )
        Spacer(modifier = Modifier.height(24.dp))
        Button(
            onClick = onRetryClick,
            modifier = Modifier.testTag("btn_retry"),
        ) {
            Icon(Icons.Default.Refresh, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Попробовать снова")
        }
    }
}

@Composable
private fun CancelledState(onStartClick: () -> Unit) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = "Отменено",
            style = MaterialTheme.typography.headlineSmall,
        )
        Spacer(modifier = Modifier.height(16.dp))
        Button(onClick = onStartClick) {
            Text("Создать новое")
        }
    }
}
