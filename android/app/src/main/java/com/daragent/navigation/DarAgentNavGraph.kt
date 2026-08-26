package com.daragent.navigation

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.daragent.presentation.auth.AuthScreen
import com.daragent.presentation.auth.LoginScreen
import com.daragent.presentation.auth.RegisterScreen
import com.daragent.presentation.brief.BriefScreen
import com.daragent.presentation.chat.ConversationScreen
import com.daragent.presentation.contacts.ContactImportScreen
import com.daragent.presentation.creategreeting.GenerationScreen
import com.daragent.presentation.creategreeting.RecommendationsScreen
import com.daragent.presentation.creategreeting.SelectOccasionScreen
import com.daragent.presentation.creategreeting.SelectPersonScreen
import com.daragent.presentation.creategreeting.SelectTemplateScreen
import com.daragent.presentation.delivery.DeliveryScreen
import com.daragent.presentation.feedback.FeedbackScreen
import com.daragent.presentation.generationprogress.GenerationProgressScreen
import com.daragent.presentation.history.HistoryScreen
import com.daragent.presentation.home.HomeScreen
import com.daragent.presentation.mascot.MascotOnboardingScreen
import com.daragent.presentation.onboarding.OnboardingScreen
import com.daragent.presentation.payment.PaymentScreen
import com.daragent.presentation.people.PeopleScreen
import com.daragent.presentation.photo.PhotoPickerScreen
import com.daragent.presentation.profile.ProfileScreen
import com.daragent.presentation.referral.ReferralScreen
import com.daragent.presentation.result.ResultScreen
import com.daragent.presentation.settings.SettingsScreen

object Routes {
    const val SPLASH = "splash"
    const val ONBOARDING = "onboarding"
    const val MASCOT_ONBOARDING = "mascot_onboarding"
    const val AUTH = "auth"
    const val LOGIN = "login"
    const val REGISTER = "register"
    const val HOME = "home"
    const val CONVERSATION = "conversation"
    const val PEOPLE = "people"
    const val PHOTO_PICKER = "photo_picker"
    const val CONTACT_IMPORT = "contact_import"

    const val SELECT_PERSON = "select_person"
    const val SELECT_OCCASION = "select_occasion"
    const val BRIEF = "brief"
    const val RECOMMENDATIONS = "recommendations"
    const val SELECT_TEMPLATE = "select_template"
    const val GENERATION = "generation"
    const val GENERATION_PROGRESS = "generation_progress"
    const val PAYMENT = "payment"
    const val DELIVERY = "delivery"
    const val RESULT = "result"

    const val PROFILE = "profile"
    const val HISTORY = "history"
    const val FEEDBACK = "feedback"
    const val REFERRAL = "referral"
    const val SETTINGS = "settings"
}

@Composable
fun DarAgentNavHost(
    navController: NavHostController,
    modifier: Modifier = Modifier,
    startDestination: String = Routes.SPLASH,
) {
    NavHost(
        navController = navController,
        startDestination = startDestination,
        modifier = modifier,
    ) {
        composable(Routes.SPLASH) {
            SplashScreen(
                onNavigateToOnboarding = {
                    navController.navigate(Routes.ONBOARDING) {
                        popUpTo(Routes.SPLASH) { inclusive = true }
                    }
                },
                onNavigateToHome = {
                    navController.navigate(Routes.HOME) {
                        popUpTo(Routes.SPLASH) { inclusive = true }
                    }
                },
                onNavigateToAuth = {
                    navController.navigate(Routes.AUTH) {
                        popUpTo(Routes.SPLASH) { inclusive = true }
                    }
                }
            )
        }

        composable(Routes.ONBOARDING) {
            OnboardingScreen(
                onComplete = {
                    navController.navigate(Routes.MASCOT_ONBOARDING) {
                        popUpTo(Routes.ONBOARDING) { inclusive = true }
                    }
                }
            )
        }

        composable(Routes.MASCOT_ONBOARDING) {
            MascotOnboardingScreen(
                onNext = {
                    navController.navigate(Routes.HOME) {
                        popUpTo(Routes.MASCOT_ONBOARDING) { inclusive = true }
                    }
                }
            )
        }

        composable(Routes.AUTH) {
            AuthScreen(
                onNavigateToLogin = { navController.navigate(Routes.LOGIN) },
                onNavigateToRegister = { navController.navigate(Routes.REGISTER) },
                onNavigateToOnboarding = {
                    navController.navigate(Routes.ONBOARDING) {
                        popUpTo(Routes.AUTH) { inclusive = true }
                    }
                }
            )
        }

        composable(Routes.LOGIN) {
            LoginScreen(
                onBack = { navController.popBackStack() },
                onNavigateToRegister = { navController.navigate(Routes.REGISTER) },
                onLoginSuccess = {
                    navController.navigate(Routes.HOME) {
                        popUpTo(Routes.AUTH) { inclusive = true }
                    }
                }
            )
        }

        composable(Routes.REGISTER) {
            RegisterScreen(
                onBack = { navController.popBackStack() },
                onRegisterSuccess = {
                    navController.navigate(Routes.HOME) {
                        popUpTo(Routes.AUTH) { inclusive = true }
                    }
                }
            )
        }

        composable(Routes.HOME) {
            HomeScreen(
                navController = navController,
                onNavigateToConversation = { navController.navigate(Routes.CONVERSATION) },
                onNavigateToPeople = { navController.navigate(Routes.PEOPLE) },
                onNavigateToProfile = { navController.navigate(Routes.PROFILE) },
                onNavigateToHistory = { navController.navigate(Routes.HISTORY) },
                onNewGreeting = { navController.navigate(Routes.SELECT_PERSON) }
            )
        }

        composable(Routes.CONVERSATION) {
            ConversationScreen(
                onBack = { navController.popBackStack() },
                onNavigateToPhoto = { navController.navigate(Routes.PHOTO_PICKER) },
                onNavigateToBrief = { navController.navigate(Routes.BRIEF) }
            )
        }

        composable(Routes.PEOPLE) {
            PeopleScreen(
                onBack = { navController.popBackStack() },
                onAddPerson = { navController.navigate(Routes.SELECT_PERSON) }
            )
        }

        composable(Routes.PHOTO_PICKER) {
            PhotoPickerScreen(
                onBack = { navController.popBackStack() },
                onPhotoSelected = { navController.popBackStack() }
            )
        }

        composable(Routes.CONTACT_IMPORT) {
            ContactImportScreen(
                onBack = { navController.popBackStack() }
            )
        }

        composable(Routes.SELECT_PERSON) {
            SelectPersonScreen(
                onNext = { navController.navigate(Routes.SELECT_OCCASION) },
                onBack = { navController.popBackStack() }
            )
        }

        composable(Routes.SELECT_OCCASION) {
            SelectOccasionScreen(
                onNext = { navController.navigate(Routes.BRIEF) },
                onBack = { navController.popBackStack() }
            )
        }

        composable(Routes.BRIEF) {
            BriefScreen(
                onNext = { navController.navigate(Routes.RECOMMENDATIONS) },
                onBack = { navController.popBackStack() }
            )
        }

        composable(Routes.RECOMMENDATIONS) {
            RecommendationsScreen(
                onNext = { navController.navigate(Routes.SELECT_TEMPLATE) },
                onBack = { navController.popBackStack() }
            )
        }

        composable(Routes.SELECT_TEMPLATE) {
            SelectTemplateScreen(
                navController = navController,
                onBack = { navController.popBackStack() }
            )
        }

        composable(Routes.GENERATION) {
            GenerationScreen(
                onBack = { navController.popBackStack() }
            )
        }

        composable(
            route = "${Routes.GENERATION_PROGRESS}/{generationId}?templateVersionId={templateVersionId}&projectId={projectId}&amount={amount}",
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
            route = "${Routes.PAYMENT}/{projectId}/{amount}",
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
                    navController.navigate(Routes.DELIVERY) {
                        popUpTo(Routes.HOME) { inclusive = false }
                    }
                }
            )
        }

        composable(Routes.DELIVERY) {
            DeliveryScreen(
                projectId = "",
                onBack = { navController.popBackStack() }
            )
        }

        composable(Routes.RESULT) {
            ResultScreen(
                onBack = { navController.popBackStack() },
                onNavigateToHome = {
                    navController.navigate(Routes.HOME) {
                        popUpTo(Routes.HOME) { inclusive = true }
                    }
                }
            )
        }

        composable(Routes.PROFILE) {
            ProfileScreen(
                onBack = { navController.popBackStack() }
            )
        }

        composable(Routes.HISTORY) {
            HistoryScreen(
                onProjectClick = { projectId, generationId ->
                    val genId = generationId ?: return@HistoryScreen.onProjectClick
                    navController.navigate("${Routes.GENERATION_PROGRESS}/$genId?projectId=$projectId")
                },
                onBack = { navController.popBackStack() }
            )
        }

        composable(
            route = "${Routes.FEEDBACK}/{projectId}",
            arguments = listOf(navArgument("projectId") { type = NavType.StringType })
        ) { backStackEntry ->
            val projectId = backStackEntry.arguments?.getString("projectId") ?: ""
            FeedbackScreen(
                projectId = projectId,
                onBack = { navController.popBackStack() }
            )
        }

        composable(Routes.REFERRAL) {
            ReferralScreen(
                onBack = { navController.popBackStack() }
            )
        }

        composable(Routes.SETTINGS) {
            SettingsScreen(
                onBack = { navController.popBackStack() },
                onExportData = { },
                onDeleteAccount = { }
            )
        }
    }
}

@Composable
private fun SplashScreen(
    onNavigateToOnboarding: () -> Unit,
    onNavigateToHome: () -> Unit,
    onNavigateToAuth: () -> Unit,
) {
}
