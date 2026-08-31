package com.daragent.presentation.chat

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.MicOff
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.daragent.presentation.chat.components.MessageBubble
import com.daragent.presentation.mascot.MascotController
import com.daragent.presentation.mascot.MascotEvent
import com.daragent.presentation.mascot.MascotRepository
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ConversationScreen(
    onBack: () -> Unit = {},
    onNavigateToPhoto: () -> Unit = {},
    onNavigateToBrief: () -> Unit = {},
    modifier: Modifier = Modifier,
    viewModel: ConversationViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsState()
    val listState = rememberLazyListState()
    val coroutineScope = rememberCoroutineScope()
    val mascotRepository = remember { MascotRepository() }

    LaunchedEffect(Unit) {
        mascotRepository.handleEvent(MascotEvent.SHOW_HELLO)
    }

    LaunchedEffect(uiState.isLoading) {
        if (uiState.isLoading) {
            mascotRepository.handleEvent(MascotEvent.ANSWER_RECEIVED)
        }
    }

    LaunchedEffect(uiState.messages.size) {
        if (uiState.messages.isNotEmpty()) {
            listState.animateScrollToItem(uiState.messages.size - 1)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text("🦊 ")
                        Text("Дарагент")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.onPrimaryContainer,
                ),
            )
        },
        bottomBar = {
            ChatInputBar(
                inputText = uiState.inputText,
                isLoading = uiState.isLoading,
                isRecording = uiState.isRecording,
                onInputChanged = viewModel::onInputTextChanged,
                onSend = viewModel::onSendMessage,
                onVoiceStart = viewModel::onVoiceRecordingStart,
                onVoiceEnd = viewModel::onVoiceRecordingEnd,
            )
        },
        modifier = modifier.testTag("conversation_screen"),
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
        ) {
            Column(modifier = Modifier.fillMaxSize()) {
                if (uiState.messages.size <= 2) {
                    MascotController(
                        repository = mascotRepository,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(180.dp),
                    )
                }

                LazyColumn(
                    state = listState,
                    modifier = Modifier
                        .fillMaxSize()
                        .testTag("message_list"),
                    contentPadding = PaddingValues(vertical = 8.dp),
                ) {
                items(
                    items = uiState.messages,
                    key = { it.id },
                ) { message ->
                    MessageBubble(
                        message = message,
                        onChipClick = viewModel::onChipSelected,
                        onActionClick = viewModel::onSuggestionAction,
                        onRetryClick = {
                            if (message is com.daragent.presentation.chat.model.Message.ErrorMessage) {
                                message.onRetry?.invoke()
                            }
                        },
                    )
                }

                if (uiState.isLoading) {
                    item {
                        TypingIndicator()
                    }
                }
                }

                if (uiState.error != null && !uiState.isLoading) {
                    Snackbar(
                        modifier = Modifier
                            .align(Alignment.BottomCenter)
                            .padding(16.dp),
                        action = {
                            TextButton(onClick = viewModel::clearError) {
                                Text("OK")
                            }
                        },
                    ) {
                        Text(uiState.error!!)
                    }
                }
            }
        }
    }
}

@Composable
private fun ChatInputBar(
    inputText: String,
    isLoading: Boolean,
    isRecording: Boolean,
    onInputChanged: (String) -> Unit,
    onSend: () -> Unit,
    onVoiceStart: () -> Unit,
    onVoiceEnd: (String?) -> Unit,
) {
    Surface(
        tonalElevation = 3.dp,
        shadowElevation = 8.dp,
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 8.dp, vertical = 8.dp)
                .navigationBarsPadding(),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            OutlinedTextField(
                value = inputText,
                onValueChange = onInputChanged,
                modifier = Modifier
                    .weight(1f)
                    .testTag("chat_input"),
                placeholder = { Text("Напиши сообщение...") },
                enabled = !isLoading,
                singleLine = false,
                maxLines = 4,
                shape = MaterialTheme.shapes.extraLarge,
            )

            Spacer(modifier = Modifier.width(8.dp))

            if (isRecording) {
                FilledIconButton(
                    onClick = { onVoiceEnd(null) },
                    modifier = Modifier.size(48.dp),
                    colors = IconButtonDefaults.filledIconButtonColors(
                        containerColor = MaterialTheme.colorScheme.error,
                    ),
                ) {
                    Icon(
                        imageVector = Icons.Default.MicOff,
                        contentDescription = "Остановить запись",
                    )
                }
            } else if (inputText.isBlank()) {
                FilledIconButton(
                    onClick = onVoiceStart,
                    modifier = Modifier.size(48.dp),
                    enabled = !isLoading,
                ) {
                    Icon(
                        imageVector = Icons.Default.Mic,
                        contentDescription = "Голосовой ввод",
                    )
                }
            } else {
                FilledIconButton(
                    onClick = onSend,
                    modifier = Modifier.size(48.dp),
                    enabled = !isLoading,
                ) {
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.Send,
                        contentDescription = "Отправить",
                    )
                }
            }
        }
    }
}

@Composable
private fun TypingIndicator() {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            text = "🦊",
            style = MaterialTheme.typography.titleLarge,
            modifier = Modifier.padding(end = 8.dp),
        )
        Surface(
            shape = MaterialTheme.shapes.medium,
            color = MaterialTheme.colorScheme.surfaceVariant,
        ) {
            Text(
                text = "Печатает...",
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}
