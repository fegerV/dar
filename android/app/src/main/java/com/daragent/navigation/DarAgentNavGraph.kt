package com.daragent.navigation

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.daragent.presentation.creategreeting.BriefScreen
import com.daragent.presentation.creategreeting.GenerationScreen
import com.daragent.presentation.creategreeting.RecommendationsScreen
import com.daragent.presentation.creategreeting.SelectOccasionScreen
import com.daragent.presentation.creategreeting.SelectPersonScreen
import com.daragent.presentation.creategreeting.SelectTemplateScreen
import com.daragent.presentation.delivery.DeliveryScreen
import com.daragent.presentation.generationprogress.GenerationProgressScreen
import com.daragent.presentation.home.HomeScreen
import com.daragent.presentation.history.HistoryScreen
import com.daragent.presentation.payment.PaymentScreen
import com.daragent.presentation.profile.ProfileScreen

object DarAgentDestinations {
    const val HOME_ROUTE = "home"
    const val SELECT_PERSON_ROUTE = "select_person"
    const val SELECT_OCCASION_ROUTE = "select_occasion"
    const val BRIEF_ROUTE = "brief"
    const val RECOMMENDATIONS_ROUTE = "recommendations"
    const val SELECT_TEMPLATE_ROUTE = "select_template"
    const val GENERATION_ROUTE = "generation"
    const val GENERATION_PROGRESS_ROUTE = "generation_progress"
    const val PAYMENT_ROUTE = "payment"
    const val DELIVERY_ROUTE = "delivery"
    const val PROFILE_ROUTE = "profile"
    const val HISTORY_ROUTE = "history"
}

@Composable
fun DarAgentNavHost(
    navController: NavHostController,
    modifier: Modifier = Modifier
) {
    NavHost(
        navController = navController,
        startDestination = DarAgentDestinations.HOME_ROUTE,
        modifier = modifier
    ) {
        composable(DarAgentDestinations.HOME_ROUTE) {
            HomeScreen(
                navController = navController,
                onNewGreeting = { navController.navigate(DarAgentDestinations.SELECT_PERSON_ROUTE) }
            )
        }

        composable(DarAgentDestinations.SELECT_PERSON_ROUTE) {
            SelectPersonScreen(onNext = { navController.navigate(DarAgentDestinations.SELECT_OCCASION_ROUTE) })
        }

        composable(DarAgentDestinations.SELECT_OCCASION_ROUTE) {
            SelectOccasionScreen(
                onNext = { navController.navigate(DarAgentDestinations.BRIEF_ROUTE) },
                onBack = { navController.popBackStack() }
            )
        }

        composable(DarAgentDestinations.BRIEF_ROUTE) {
            BriefScreen(
                onNext = { navController.navigate(DarAgentDestinations.RECOMMENDATIONS_ROUTE) },
                onBack = { navController.popBackStack() }
            )
        }

        composable(DarAgentDestinations.RECOMMENDATIONS_ROUTE) {
            RecommendationsScreen(
                onNext = { navController.navigate(DarAgentDestinations.SELECT_TEMPLATE_ROUTE) },
                onBack = { navController.popBackStack() }
            )
        }

        composable(DarAgentDestinations.SELECT_TEMPLATE_ROUTE) {
            SelectTemplateScreen(
                navController = navController,
                onBack = { navController.popBackStack() }
            )
        }

        composable(DarAgentDestinations.GENERATION_ROUTE) {
            GenerationScreen(onBack = { navController.popBackStack() })
        }

        composable(
            route = "${DarAgentDestinations.GENERATION_PROGRESS_ROUTE}/{generationId}?templateVersionId={templateVersionId}&projectId={projectId}&amount={amount}",
            arguments = listOf(
                navArgument("generationId") { type = NavType.StringType },
                navArgument("templateVersionId") { type = NavType.StringType },
                navArgument("projectId") { type = NavType.StringType },
                navArgument("amount") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val generationId = backStackEntry.arguments?.getString("generationId") ?: return@composable
            GenerationProgressScreen(
                generationId = generationId,
                onBack = { navController.popBackStack() }
            )
        }

        composable(
            route = "${DarAgentDestinations.PAYMENT_ROUTE}/{projectId}/{amount}",
            arguments = listOf(
                navArgument("projectId") { type = NavType.StringType },
                navArgument("amount") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val projectId = backStackEntry.arguments?.getString("projectId") ?: return@composable
            val amount = backStackEntry.arguments?.getString("amount")?.toDoubleOrNull() ?: 0.0
            PaymentScreen(
                projectId = projectId,
                amount = amount,
                navController = navController,
                onBack = { navController.popBackStack() },
                onSuccess = {
                    navController.navigate(DarAgentDestinations.DELIVERY_ROUTE) {
                        popUpTo(DarAgentDestinations.HOME_ROUTE) { inclusive = false }
                    }
                }
            )
        }

        composable(DarAgentDestinations.DELIVERY_ROUTE) {
            DeliveryScreen(projectId = "", onBack = { navController.popBackStack() })
        }

        composable(DarAgentDestinations.PROFILE_ROUTE) {
            ProfileScreen(onBack = { navController.popBackStack() })
        }

        composable(DarAgentDestinations.HISTORY_ROUTE) {
            HistoryScreen(
                onProjectClick = { projectId ->
                    navController.navigate("${DarAgentDestinations.GENERATION_PROGRESS_ROUTE}/$projectId")
                },
                onBack = { navController.popBackStack() }
            )
        }
    }
}
