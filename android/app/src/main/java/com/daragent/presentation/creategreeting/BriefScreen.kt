package com.daragent.presentation.creategreeting

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Slider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.daragent.presentation.mascot.MascotEvent
import com.daragent.presentation.mascot.MascotRepository
import com.daragent.presentation.mascot.MascotView
import com.daragent.presentation.mascot.MascotRepository
import com.daragent.presentation.mascot.MascotView
import com.daragent.presentation.mascot.MascotEvent

@Composable
fun BriefScreen(
    viewModel: CreateGreetingViewModel = viewModel(),
    onNext: () -> Unit = {},
    onBack: () -> Unit = {}
) {
    val state by viewModel.state.collectAsState()
    var mood by remember { mutableStateOf(state.brief?.desiredMood ?: "") }
    var insideJoke by remember { mutableStateOf(state.brief?.insideJoke ?: "") }
    var hobbies by remember { mutableStateOf(state.brief?.hobbiesText ?: "") }
    var traits by remember { mutableStateOf(state.brief?.characterTraits ?: "") }
    var story by remember { mutableStateOf(state.brief?.memorableStory ?: "") }
    var message by remember { mutableStateOf(state.brief?.senderMessage ?: "") }
    var humor by remember { mutableStateOf(state.brief?.humorLevel?.toFloat() ?: 50f) }
    var emotion by remember { mutableStateOf(state.brief?.emotionLevel?.toFloat() ?: 50f) }

    val mascotRepository = remember { MascotRepository() }
    LaunchedEffect(Unit) {
        mascotRepository.handleEvent(MascotEvent.SAVE_STARTED, "Расскажите о получателе")
    }

    Row(modifier = Modifier.fillMaxSize(), horizontalArrangement = Arrangement.SpaceBetween) {
        MascotView(
            modifier = Modifier.weight(1f),
        )
        Column(modifier = Modifier.weight(1f)) {
        Text(text = "Расскажите о получателе", modifier = Modifier.padding(16.dp))
        OutlinedTextField(value = mood, onValueChange = { mood = it }, label = { Text("Настроение") }, modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp))
        OutlinedTextField(value = insideJoke, onValueChange = { insideJoke = it }, label = { Text("Внутренняя шутка") }, modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp))
        OutlinedTextField(value = hobbies, onValueChange = { hobbies = it }, label = { Text("Хобби") }, modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp))
        OutlinedTextField(value = traits, onValueChange = { traits = it }, label = { Text("Черты характера") }, modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp))
        OutlinedTextField(value = story, onValueChange = { story = it }, label = { Text("Памятная история") }, modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp))
        OutlinedTextField(value = message, onValueChange = { message = it }, label = { Text("Ваше сообщение") }, modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp))
        Text(text = "Юмор: ${humor.toInt()}", modifier = Modifier.padding(start = 16.dp, end = 16.dp, top = 8.dp))
        Slider(value = humor, onValueChange = { humor = it }, valueRange = 0f..100f, modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp))
        Text(text = "Эмоции: ${emotion.toInt()}", modifier = Modifier.padding(start = 16.dp, end = 16.dp, top = 8.dp))
        Slider(value = emotion, onValueChange = { emotion = it }, valueRange = 0f..100f, modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp))
        Button(onClick = {
            viewModel.updateBrief(
                com.daragent.domain.model.Brief(
                    id = state.brief?.id ?: "",
                    projectId = state.project?.id ?: "",
                    status = state.brief?.status ?: "draft",
                    occasionText = null,
                    senderRole = null,
                    recipientRole = null,
                    relationship = null,
                    desiredMood = mood,
                    humorLevel = humor.toInt(),
                    emotionLevel = emotion.toInt(),
                    surpriseLevel = null,
                    insideJoke = insideJoke,
                    hobbiesText = hobbies,
                    characterTraits = traits,
                    memorableStory = story,
                    desiredPhrase = null,
                    forbiddenTopics = null,
                    senderMessage = message
                )
            )
            mascotRepository.handleEvent(com.daragent.presentation.mascot.MascotEvent.SAVE_COMPLETED, "Готово! Получить рекомендации?")
            viewModel.completeBrief()
            onNext()
        }, modifier = Modifier.padding(16.dp)) {
            Text("Получить рекомендации")
        }
        Button(onClick = onBack, modifier = Modifier.padding(16.dp)) {
            Text("Назад")
        }
    }
}
