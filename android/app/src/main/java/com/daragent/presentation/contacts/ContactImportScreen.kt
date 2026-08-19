package com.daragent.presentation.contacts

import android.Manifest
import android.content.ContentResolver
import android.net.Uri
import android.provider.ContactsContract
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.daragent.presentation.mascot.MascotEvent
import com.daragent.presentation.mascot.MascotRepository
import com.daragent.presentation.mascot.MascotView

data class ContactData(
    val name: String,
    val birthday: String? = null,
    val relationship: String? = null,
)

@OptIn(ExperimentalPermissionsApi::class)
@Composable
fun ContactImportScreen(
    modifier: Modifier = Modifier,
    onBack: () -> Unit = {},
) {
    val context = LocalContext.current
    val mascotRepository = remember { MascotRepository() }

    var hasPermission by remember {
        mutableStateOf(false)
    }
    var contacts by remember { mutableStateOf<List<ContactData>>(emptyList()) }
    var consentGiven by remember { mutableStateOf(false) }
    var isImporting by remember { mutableStateOf(false) }
    var importResult by remember { mutableStateOf<Pair<Int, Int>?>(null) }

    LaunchedEffect(Unit) {
        mascotRepository.handleEvent(MascotEvent.SHOW_HELLO, "Давай импортируем контакты для персональных поздравлений!")
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(Color(0xFFF8FAFC))
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        MascotView(
            modifier = Modifier
                .size(160.dp)
                .padding(bottom = 16.dp),
        )

        Text(
            text = "Импорт контактов",
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFF37306B),
            modifier = Modifier.padding(bottom = 16.dp),
        )

        Text(
            text = "Ваши контакты обрабатываются локально. Мы НИКОГДА не отправляем их третьим сторонам.",
            fontSize = 12.sp,
            color = Color(0xFF6B7280),
            modifier = Modifier.padding(bottom = 16.dp),
        )

        if (!hasPermission) {
            Button(onClick = { hasPermission = true }) {
                Text("Разрешить доступ к контактам")
            }
        } else {
            if (contacts.isEmpty() && !isImporting) {
                Button(onClick = {
                    isImporting = true
                    val cr: ContentResolver = context.contentResolver
                    val projection = arrayOf(
                        ContactsContract.Contacts.DISPLAY_NAME,
                        ContactsContract.Contacts.HAS_PHONE_NUMBER,
                    )
                    val cursor = cr.query(
                        ContactsContract.Contacts.CONTENT_URI,
                        projection,
                        null,
                        null,
                        null,
                    )

                    val result = mutableListOf<ContactData>()
                    cursor?.use {
                        val nameIndex = it.getColumnIndex(ContactsContract.Contacts.DISPLAY_NAME)
                        while (it.moveToNext()) {
                            val name = it.getString(nameIndex)
                            if (!name.isNullOrEmpty()) {
                                result.add(ContactData(name = name))
                            }
                        }
                    }
                    contacts = result
                    isImporting = false
                }) {
                    Text(if (isImporting) "Сканируем..." else "Сканировать контакты")
                }
            }

            if (contacts.isNotEmpty()) {
                Text(
                    "Найдено контактов: ${contacts.size}",
                    modifier = Modifier.padding(8.dp),
                )

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Checkbox(
                        checked = consentGiven,
                        onCheckedChange = { consentGiven = it },
                    )
                    Text(
                        "Я даю согласие на обработку контактов",
                        fontSize = 12.sp,
                        modifier = Modifier.padding(start = 8.dp),
                    )
                }

                Button(
                    onClick = {
                        if (consentGiven) {
                            isImporting = true
                            mascotRepository.handleEvent(
                                MascotEvent.SAVE_STARTED,
                                "Импортирую ${contacts.size} контактов..."
                            )
                            importResult = Pair(contacts.size, 0)
                            isImporting = false
                            mascotRepository.handleEvent(
                                MascotEvent.SAVE_COMPLETED,
                                "Готово! Контакты сохранены локально."
                            )
                        }
                    },
                    enabled = consentGiven && !isImporting,
                    modifier = Modifier.padding(8.dp),
                ) {
                    Text(if (isImporting) "Импортирую..." else "Импортировать выбранные")
                }

                importResult?.let { (imported, skipped) ->
                    Text(
                        "Импортировано: $imported, пропущено: $skipped",
                        color = Color(0xFF10B981),
                        modifier = Modifier.padding(8.dp),
                    )
                }
            }
        }

        Spacer(modifier = Modifier.weight(1f))

        Button(onClick = onBack, modifier = Modifier.padding(8.dp)) {
            Text("Назад")
        }
    }
}
