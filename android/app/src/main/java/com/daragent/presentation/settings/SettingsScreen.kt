package com.daragent.presentation.settings

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
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
import com.daragent.presentation.mascot.MascotEvent
import com.daragent.presentation.mascot.MascotRepository
import com.daragent.presentation.mascot.MascotView

@Composable
fun SettingsScreen(
    modifier: Modifier = Modifier,
    onBack: () -> Unit = {},
    onExportData: () -> Unit = {},
    onDeleteAccount: () -> Unit = {},
) {
    val mascotRepository = remember { MascotRepository() }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(Color(0xFFF8FAFC))
            .padding(16.dp),
    ) {
        MascotView(
            modifier = Modifier
                .fillMaxWidth()
                .height(160.dp),
        )

        Text(
            text = "Настройки",
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFF37306B),
            modifier = Modifier.padding(vertical = 16.dp),
        )

        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp),
            shape = RoundedCornerShape(12.dp),
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Экспорт данных (GDPR)", fontWeight = FontWeight.Bold)
                Text("Скачайте все ваши данные", fontSize = 12.sp, color = Color(0xFF6B7280))
                Spacer(modifier = Modifier.height(8.dp))
                Button(onClick = {
                    onExportData()
                    mascotRepository.handleEvent(MascotEvent.SHARE_COMPLETED, "Данные экспортированы!")
                }, modifier = Modifier.align(Alignment.End)) {
                    Text("Экспорт")
                }
            }
        }

        var showDeleteDialog by remember { mutableStateOf(false) }

        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp),
            shape = RoundedCornerShape(12.dp),
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Удалить аккаунт", fontWeight = FontWeight.Bold, color = Color.Red)
                Text(
                    "Безвозвратно удалит все ваши данные",
                    fontSize = 12.sp,
                    color = Color(0xFF6B7280),
                )
                Spacer(modifier = Modifier.height(8.dp))
                Button(
                    onClick = { showDeleteDialog = true },
                    modifier = Modifier.align(Alignment.End),
                    colors = ButtonDefaults.buttonColors(containerColor = Color.Red),
                ) {
                    Text("Удалить")
                }
            }
        }

        if (showDeleteDialog) {
            AlertDialog(
                onDismissRequest = { showDeleteDialog = false },
                title = { Text("Точно удалить аккаунт?") },
                text = { Text("Это действие нельзя отменить. Все данные будут удалены в течение 30 дней.") },
                confirmButton = {
                    TextButton(onClick = {
                        showDeleteDialog = false
                        onDeleteAccount()
                        mascotRepository.handleEvent(MascotEvent.ANSWER_RECEIVED, "Аккаунт помечен к удалению.")
                    }) {
                        Text("Удалить", color = Color.Red)
                    }
                },
                dismissButton = {
                    TextButton(onClick = { showDeleteDialog = false }) {
                        Text("Отмена")
                    }
                },
            )
        }

        Spacer(modifier = Modifier.weight(1f))
        Button(onClick = onBack, modifier = Modifier.padding(16.dp)) {
            Text("Назад")
        }
    }
}
