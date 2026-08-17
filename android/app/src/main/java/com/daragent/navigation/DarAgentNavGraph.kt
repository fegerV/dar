package com.daragent.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.daragent.presentation.home.HomeScreen

object DarAgentDestinations {
    const val HOME_ROUTE = "home"
    const val PEOPLE_ROUTE = "people"
    const val CREATE_GREETING_ROUTE = "create_greeting"
    const val TEMPLATES_ROUTE = "templates"
    const val GENERATION_ROUTE = "generation"
    const val PAYMENT_ROUTE = "payment"
    const val PROFILE_ROUTE = "profile"
}

@Composable
fun DarAgentNavGraph(navController: NavHostController) {
    NavHost(navController = navController, startDestination = DarAgentDestinations.HOME_ROUTE) {
        composable(DarAgentDestinations.HOME_ROUTE) { HomeScreen() }
    }
}
