package com.daragent.presentation.people

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.daragent.core.network.model.PersonDto
import com.daragent.presentation.people.components.EmptyPeopleState
import com.daragent.presentation.people.components.PersonCard

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PeopleScreen(
    onBack: () -> Unit = {},
    onAddPerson: () -> Unit = {},
    viewModel: PeopleViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Мои люди") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.Close, contentDescription = "Закрыть")
                    }
                },
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = { viewModel.showCreateDialog() },
                modifier = Modifier.testTag("fab_add_person"),
            ) {
                Icon(Icons.Default.Add, contentDescription = "Добавить")
            }
        },
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding),
        ) {
            when {
                uiState.isLoading -> {
                    CircularProgressIndicator(
                        modifier = Modifier.align(Alignment.Center),
                    )
                }
                uiState.people.isEmpty() -> {
                    EmptyPeopleState(
                        onCreateClick = { viewModel.showCreateDialog() },
                    )
                }
                else -> {
                    LazyColumn(
                        modifier = Modifier
                            .fillMaxSize()
                            .testTag("people_list"),
                        contentPadding = PaddingValues(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp),
                    ) {
                        items(
                            items = uiState.people,
                            key = { it.id },
                        ) { person ->
                            PersonCard(
                                person = person,
                                onClick = { },
                            )
                        }
                    }
                }
            }
        }
    }

    if (uiState.showCreateDialog) {
        CreatePersonDialog(
            name = uiState.createName,
            relationship = uiState.createRelationship,
            birthDate = uiState.createBirthDate,
            interests = uiState.createInterests,
            notes = uiState.createNotes,
            isCreating = uiState.isCreating,
            onNameChange = { viewModel.updateCreateName(it) },
            onRelationshipChange = { viewModel.updateCreateRelationship(it) },
            onBirthDateChange = { viewModel.updateCreateBirthDate(it) },
            onInterestsChange = { viewModel.updateCreateInterests(it) },
            onNotesChange = { viewModel.updateCreateNotes(it) },
            onConfirm = { viewModel.createPerson() },
            onDismiss = { viewModel.hideCreateDialog() },
        )
    }
}

@Composable
private fun CreatePersonDialog(
    name: String,
    relationship: String,
    birthDate: String,
    interests: String,
    notes: String,
    isCreating: Boolean,
    onNameChange: (String) -> Unit,
    onRelationshipChange: (String) -> Unit,
    onBirthDateChange: (String) -> Unit,
    onInterestsChange: (String) -> Unit,
    onNotesChange: (String) -> Unit,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit,
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Добавить человека") },
        text = {
            Column(
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                OutlinedTextField(
                    value = name,
                    onValueChange = onNameChange,
                    label = { Text("Имя") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                )
                OutlinedTextField(
                    value = relationship,
                    onValueChange = onRelationshipChange,
                    label = { Text("Кто он/она вам") },
                    placeholder = { Text("Мама, друг, коллега...") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                )
                OutlinedTextField(
                    value = birthDate,
                    onValueChange = onBirthDateChange,
                    label = { Text("Дата рождения") },
                    placeholder = { Text("ДД.ММ.ГГГГ") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                )
                OutlinedTextField(
                    value = interests,
                    onValueChange = onInterestsChange,
                    label = { Text("Интересы") },
                    placeholder = { Text("Через запятую") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                )
                OutlinedTextField(
                    value = notes,
                    onValueChange = onNotesChange,
                    label = { Text("Заметки") },
                    modifier = Modifier.fillMaxWidth(),
                    minLines = 2,
                    maxLines = 3,
                )
            }
        },
        confirmButton = {
            Button(
                onClick = onConfirm,
                enabled = name.isNotBlank() && !isCreating,
            ) {
                if (isCreating) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(20.dp),
                        color = MaterialTheme.colorScheme.onPrimary,
                    )
                } else {
                    Text("Добавить")
                }
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Отмена")
            }
        },
        modifier = Modifier.testTag("dialog_create_person"),
    )
}
