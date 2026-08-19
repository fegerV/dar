package com.daragent.presentation.mascot

import androidx.compose.foundation.layout.*
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun MascotOnboardingScreen(
    modifier: Modifier = Modifier,
    mascotRepository: MascotRepository = androidx.compose.runtime.remember { MascotRepository() },
    onNext: () -> Unit = {},
) {
    LaunchedEffect(Unit) {
        mascotRepository.handleEvent(MascotEvent.SHOW_HELLO, "Привет! Меня зовут Дарагент. Я твой личный агент по поздравлениям. Давай познакомимся! Как тебя зовут?")
    }

    Column(
        modifier = modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.SpaceBetween,
    ) {
        MascotView(
            modifier = Modifier
                .fillMaxWidth()
                .height(240.dp)
                .padding(top = 32.dp),
        )

        Button(
            onClick = {
                mascotRepository.handleEvent(MascotEvent.SAVE_COMPLETED, "Отлично! Перейдем к следующему шагу.")
                onNext()
            },
            modifier = Modifier.padding(16.dp),
        ) {
            Text("Начать")
        }
    }
}
