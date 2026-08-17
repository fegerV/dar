package com.daragent.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.daragent.presentation.creategreeting.BriefScreen
import com.daragent.presentation.creategreeting.GenerationScreen
import com.daragent.presentation.creategreeting.RecommendationsScreen
import com.daragent.presentation.creategreeting.SelectOccasionScreen
import com.daragent.presentation.creategreeting.SelectPersonScreen
import com.daragent.presentation.creategreeting.SelectTemplateScreen
import com.daragent.presentation.generationprogress.GenerationProgressScreen
import com.daragent.presentation.home.HomeScreen
import com.daragent.presentation.payment.PaymentScreen

object DarAgentDestinations {
    const val HOME_ROUTE = "home"
    const val PEOPLE_ROUTE = "people"
    const val CREATE_GREETING_ROUTE = "create_greeting"
    const val SELECT_PERSON_ROUTE = "select_person"
    const val SELECT_OCCASION_ROUTE = "select_occasion"
    const val BRIEF_ROUTE = "brief"
    const val RECOMMENDATIONS_ROUTE = "recommendations"
    const val SELECT_TEMPLATE_ROUTE = "select_template"
    const val GENERATION_ROUTE = "generation"
    const val GENERATION_PROGRESS_ROUTE = "generation_progress"
    const val PAYMENT_ROUTE = "payment"
    const val TEMPLATES_ROUTE = "templates"
    const val PAYMENT_ROUTE = "payment"
    const val PROFILE_ROUTE = "profile"
}

@Composable
fun DarAgentNavGraph(navController: NavHostController) {
    NavHost(navController = navController, startDestination = DarAgentDestinations.HOME_ROUTE) {
        composable(DarAgentDestinations.HOME_ROUTE) { HomeScreen(navController) }
        composable(DarAgentDestinations.SELECT_PERSON_ROUTE) { SelectPersonScreen(onNext = { navController.navigate(DarAgentDestinations.SELECT_OCCASION_ROUTE) }) }
        composable(DarAgentDestinations.SELECT_OCCASION_ROUTE) { SelectOccasionScreen(onNext = { navController.navigate(DarAgentDestinations.BRIEF_ROUTE) }, onBack = { navController.popBackStack() }) }
        composable(DarAgentDestinations.BRIEF_ROUTE) { BriefScreen(onNext = { navController.navigate(DarAgentDestinations.RECOMMENDATIONS_ROUTE) }, onBack = { navController.popBackStack() }) }
        composable(DarAgentDestinations.RECOMMENDATIONS_ROUTE) { RecommendationsScreen(onNext = { navController.navigate(DarAgentDestinations.SELECT_TEMPLATE_ROUTE) }, onBack = { navController.popBackStack() }) }
        composable(DarAgentDestinations.SELECT_TEMPLATE_ROUTE) { SelectTemplateScreen(onNext = { navController.navigate(DarAgentDestinations.GENERATION_ROUTE) }, onBack = { navController.popBackStack() }) }
        composable(DarAgentDestinations.GENERATION_ROUTE) { GenerationScreen(onBack = { navController.popBackStack() }) }
        composable("${DarAgentDestinations.GENERATION_PROGRESS_ROUTE}/{generationId}") { backStackEntry ->
            val generationId = backStackEntry.arguments?.getString("generationId") ?: return@composable
            val accessToken = ""
            GenerationProgressScreen(generationId = generationId, accessToken = accessToken, onBack = { navController.popBackStack() })
        }
        composable("${DarAgentDestinations.PAYMENT_ROUTE}/{projectId}/{amount}") { backStackEntry ->
            val projectId = backStackEntry.arguments?.getString("projectId") ?: return@composable
            val amount = backStackEntry.arguments?.getString("amount")?.toDoubleOrNull() ?: 0.0
            PaymentScreen(projectId = projectId, amount = amount, onBack = { navController.popBackStack() }, onSuccess = { navController.popBackStack() })
        }
    }
}
