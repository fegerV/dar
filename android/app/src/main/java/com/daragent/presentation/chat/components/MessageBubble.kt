package com.daragent.presentation.chat.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.daragent.presentation.chat.model.Message
import com.daragent.presentation.chat.model.SuggestionAction

@Composable
fun MessageBubble(
    message: Message,
    onChipClick: (String) -> Unit = {},
    onActionClick: (SuggestionAction) -> Unit = {},
    onPhotoClick: () -> Unit = {},
    onRetryClick: () -> Unit = {},
    modifier: Modifier = Modifier,
) {
    when (message) {
        is Message.Text -> TextMessageBubble(message = message, modifier = modifier)
        is Message.Welcome -> WelcomeMessage(message = message, modifier = modifier)
        is Message.QuickChips -> QuickChipsMessage(
            message = message,
            onChipClick = onChipClick,
            modifier = modifier,
        )
        is Message.SuggestionCard -> SuggestionCard(
            message = message,
            onActionClick = onActionClick,
            modifier = modifier,
        )
        is Message.PhotoRequest -> PhotoRequestBubble(
            message = message,
            onPhotoClick = onPhotoClick,
            modifier = modifier,
        )
        is Message.PhotoCard -> PhotoCard(message = message, modifier = modifier)
        is Message.VideoCard -> VideoCard(message = message, modifier = modifier)
        is Message.GenerationProgress -> GenerationProgressBubble(
            message = message,
            modifier = modifier,
        )
        is Message.ErrorMessage -> ErrorBubble(
            message = message,
            onRetryClick = onRetryClick,
            modifier = modifier,
        )
        is Message.ShareRequest -> ShareRequestBubble(
            message = message,
            onPhotoClick = onPhotoClick,
            modifier = modifier,
        )
    }
}

@Composable
private fun TextMessageBubble(
    message: Message.Text,
    modifier: Modifier = Modifier,
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 4.dp),
        horizontalArrangement = if (message.isFromUser) Arrangement.End else Arrangement.Start,
    ) {
        if (!message.isFromUser) {
            Text(
                text = "🦊",
                style = MaterialTheme.typography.titleLarge,
                modifier = Modifier.padding(end = 8.dp),
            )
        }
        Surface(
            shape = RoundedCornerShape(
                topStart = 16.dp,
                topEnd = 16.dp,
                bottomStart = if (message.isFromUser) 16.dp else 4.dp,
                bottomEnd = if (message.isFromUser) 4.dp else 16.dp,
            ),
            color = if (message.isFromUser) {
                MaterialTheme.colorScheme.primary
            } else {
                MaterialTheme.colorScheme.surfaceVariant
            },
            modifier = Modifier.widthIn(max = 280.dp),
        ) {
            Text(
                text = message.text,
                modifier = Modifier.padding(12.dp),
                color = if (message.isFromUser) {
                    MaterialTheme.colorScheme.onPrimary
                } else {
                    MaterialTheme.colorScheme.onSurfaceVariant
                },
            )
        }
    }
}

@Composable
private fun WelcomeMessage(
    message: Message.Welcome,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            text = "🦊",
            style = MaterialTheme.typography.displayMedium,
        )
        Spacer(modifier = Modifier.height(12.dp))
        Text(
            text = if (message.userName != null) {
                "Привет, ${message.userName}! ❤️"
            } else {
                "Привет! Я Дарагент 🦊"
            },
            style = MaterialTheme.typography.headlineSmall,
            textAlign = TextAlign.Center,
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = "Кого сегодня поздравляем?",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center,
        )
    }
}

@Composable
private fun QuickChipsMessage(
    message: Message.QuickChips,
    onChipClick: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
    ) {
        FlowRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            message.chips.forEach { chip ->
                AssistChip(
                    onClick = { onChipClick(chip) },
                    label = { Text(chip) },
                    modifier = Modifier.testTag("chip_$chip"),
                )
            }
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun FlowRow(
    modifier: Modifier = Modifier,
    horizontalArrangement: Arrangement.Horizontal = Arrangement.Start,
    verticalArrangement: Arrangement.Vertical = Arrangement.Top,
    content: @Composable () -> Unit,
) {
    androidx.compose.foundation.layout.FlowRow(
        modifier = modifier,
        horizontalArrangement = horizontalArrangement,
        verticalArrangement = verticalArrangement,
    ) {
        content()
    }
}

@Composable
private fun SuggestionCard(
    message: Message.SuggestionCard,
    onActionClick: (SuggestionAction) -> Unit,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface,
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
        ) {
            Text(
                text = message.title,
                style = MaterialTheme.typography.titleMedium,
            )
            if (message.subtitle != null) {
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = message.subtitle,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            if (message.actions.isNotEmpty()) {
                Spacer(modifier = Modifier.height(12.dp))
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    message.actions.forEach { action ->
                        OutlinedButton(
                            onClick = { onActionClick(action) },
                            modifier = Modifier.testTag("action_${action.label}"),
                        ) {
                            Text(action.label)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun PhotoRequestBubble(
    message: Message.PhotoRequest,
    onPhotoClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        if (message.text != null) {
            Text(
                text = message.text,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Spacer(modifier = Modifier.height(8.dp))
        }
        Button(
            onClick = onPhotoClick,
            modifier = Modifier.testTag("btn_upload_photo"),
        ) {
            Text("📸 Загрузить фото")
        }
    }
}

@Composable
private fun PhotoCard(
    message: Message.PhotoCard,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        shape = RoundedCornerShape(16.dp),
    ) {
        Column {
            AsyncImage(
                model = message.photoUrl,
                contentDescription = null,
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(max = 200.dp)
                    .clip(RoundedCornerShape(topStart = 16.dp, topEnd = 16.dp)),
                contentScale = ContentScale.Crop,
            )
            if (message.caption != null) {
                Text(
                    text = message.caption,
                    modifier = Modifier.padding(12.dp),
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
        }
    }
}

@Composable
private fun VideoCard(
    message: Message.VideoCard,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp)
            .testTag("video_card"),
        shape = RoundedCornerShape(16.dp),
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(200.dp)
                .background(Color.Black),
            contentAlignment = Alignment.Center,
        ) {
            AsyncImage(
                model = message.thumbnailUrl ?: message.videoUrl,
                contentDescription = null,
                modifier = Modifier.fillMaxSize(),
                contentScale = ContentScale.Crop,
            )
            Icon(
                imageVector = androidx.compose.material.icons.Icons.Default.PlayArrow,
                contentDescription = "Play",
                tint = Color.White,
                modifier = Modifier.size(64.dp),
            )
        }
    }
}

@Composable
private fun GenerationProgressBubble(
    message: Message.GenerationProgress,
    modifier: Modifier = Modifier,
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            text = "🦊",
            style = MaterialTheme.typography.titleLarge,
            modifier = Modifier.padding(end = 8.dp),
        )
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = message.message,
                style = MaterialTheme.typography.bodyMedium,
            )
            Spacer(modifier = Modifier.height(4.dp))
            LinearProgressIndicator(
                progress = { message.progress / 100f },
                modifier = Modifier.fillMaxWidth(),
            )
        }
    }
}

@Composable
private fun ErrorBubble(
    message: Message.ErrorMessage,
    onRetryClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.errorContainer,
        ),
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
        ) {
            Text(
                text = message.text,
                color = MaterialTheme.colorScheme.onErrorContainer,
            )
            if (message.onRetry != null) {
                Spacer(modifier = Modifier.height(8.dp))
                TextButton(onClick = onRetryClick) {
                    Text("Повторить")
                }
            }
        }
    }
}

@Composable
private fun ShareRequestBubble(
    message: Message.ShareRequest,
    onPhotoClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            text = "🎉 Поздравление готово!",
            style = MaterialTheme.typography.titleMedium,
        )
        Spacer(modifier = Modifier.height(12.dp))
        Button(
            onClick = onPhotoClick,
            modifier = Modifier.testTag("btn_share"),
        ) {
            Text("📤 Отправить")
        }
    }
}
