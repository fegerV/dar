package com.daragent.presentation.mascot

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.animation.core.EaseInOut
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalInspectionMode
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun MascotController(
    repository: MascotRepository,
    modifier: Modifier = Modifier,
    onStateChange: ((MascotState) -> Unit)? = null,
) {
    val currentState by repository.currentState.collectAsState()
    val bubbleContent by repository.bubbleContent.collectAsState()

    LaunchedEffect(currentState) {
        onStateChange?.invoke(currentState)
    }

    Box(modifier = modifier.fillMaxSize()) {
        MascotRiveView(
            state = currentState,
            modifier = Modifier
                .align(Alignment.Center)
                .size(180.dp),
        )

        bubbleContent?.let { content ->
            MascotBubble(
                content = content,
                modifier = Modifier
                    .align(Alignment.TopCenter)
                    .padding(top = 32.dp, start = 32.dp, end = 32.dp),
            )
        }
    }
}

@Composable
fun MascotBubble(
    content: MascotBubbleContent,
    modifier: Modifier = Modifier,
) {
    val displayText = content.text

    if (displayText != null) {
        Surface(
            modifier = modifier
                .wrapContentSize()
                .padding(4.dp),
            shape = RoundedCornerShape(16.dp),
            tonalElevation = 4.dp,
            color = Color(0xFFF0F4FF),
        ) {
            Text(
                text = displayText,
                fontSize = 14.sp,
                fontWeight = FontWeight.Normal,
                color = Color(0xFF37306B),
                modifier = Modifier.padding(12.dp),
            )
        }
    }
}

@Composable
fun MascotRiveView(
    state: MascotState,
    modifier: Modifier = Modifier,
) {
    val emoji = when (state) {
        is MascotState.Hello -> "👋"
        is MascotState.Listen -> "👂"
        is MascotState.Think -> "🤔"
        is MascotState.Write -> "✍️"
        is MascotState.Read -> "📖"
        is MascotState.LookUp -> "👀"
        is MascotState.Happy -> "😊"
        is MascotState.Surprised -> "😮"
        is MascotState.Wink -> "😉"
        is MascotState.Point -> "👉"
        is MascotState.Celebrate -> "🎉"
        is MascotState.Working -> "⚙️"
        is MascotState.Success -> "✅"
        is MascotState.Error -> "❌"
        is MascotState.Sorry -> "😔"
        is MascotState.Goodbye -> "👋"
        else -> "🦊"
    }

    val infiniteTransition = rememberInfiniteTransition(label = "mascot_pulse")
    val scale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = if (state.isLoop) 1.1f else 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = EaseInOut),
            repeatMode = RepeatMode.Reverse,
        ),
        label = "scale",
    )

    Box(
        modifier = modifier,
        contentAlignment = Alignment.Center,
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
        ) {
            Text(
                text = emoji,
                fontSize = (64 * scale).sp,
            )
            if (state.riveStateName != "idle") {
                Text(
                    text = state.riveStateName,
                    fontSize = 12.sp,
                    color = Color.Gray,
                )
            }
        }
    }
}
