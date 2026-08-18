package com.daragent.presentation.home

import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import com.daragent.navigation.DarAgentDestinations

data class BottomNavItem(
    val route: String,
    val title: String
)

@Composable
fun getBottomNavItems(): List<BottomNavItem> {
    return listOf(
        BottomNavItem(DarAgentDestinations.HOME_ROUTE, "Главная"),
        BottomNavItem(DarAgentDestinations.HISTORY_ROUTE, "История"),
        BottomNavItem(DarAgentDestinations.PROFILE_ROUTE, "Профиль")
    )
}

@Composable
fun MainScreen(navController: NavHostController) {
    val items = getBottomNavItems()
    var selectedItem by rememberSaveable { mutableStateOf(items.first().route) }

    Scaffold(
        bottomBar = {
            NavigationBar {
                items.forEach { item ->
                    NavigationBarItem(
                        selected = selectedItem == item.route,
                        onClick = {
                            selectedItem = item.route
                            navController.navigate(item.route) {
                                popUpTo(navController.graph.startDestinationId) { saveState = true }
                                launchSingleTop = true
                                restoreState = true
                            }
                        },
                        icon = {
                            Text(item.title.first().toString())
                        },
                        label = { Text(item.title) }
                    )
                }
            }
        }
    ) { innerPadding ->
        DarAgentNavHost(
            navController = navController,
            modifier = Modifier.padding(innerPadding)
        )
    }
}
