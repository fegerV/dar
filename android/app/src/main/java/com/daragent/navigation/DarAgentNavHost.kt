package com.daragent.navigation

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.daragent.presentation.onboarding.OnboardingScreen
import com.daragent.presentation.home.HomeScreen
import com.daragent.presentation.auth.AuthScreen
import com.daragent.presentation.auth.LoginScreen
import com.daragent.presentation.auth.RegisterScreen
import com.daragent.presentation.chat.ConversationScreen
import com.daragent.presentation.people.PeopleScreen
import com.daragent.presentation.photo.PhotoPickerScreen
import com.daragent.presentation.brief.BriefScreen
import com.daragent.presentation.generation.GenerationScreen
import com.daragent.presentation.result.ResultScreen
import com.daragent.presentation.payment.PaymentScreen
import com.daragent.presentation.profile.ProfileScreen

object Routes {
    const val SPLASH = "splash"
    const val ONBOARDING = "onboarding"
    const val AUTH = "auth"
    const val LOGIN = "login"
    const val REGISTER = "register"
    const val HOME = "home"
    const val CONVERSATION = "conversation"
    const val PEOPLE = "people"
    const val PHOTO_PICKER = "photo_picker"
    const val BRIEF = "brief"
    const val GENERATION = "generation"
    const val RESULT = "result"
    const val PAYMENT = "payment"
    const val PROFILE = "profile"
}

@Composable
fun DarAgentNavHost(
    modifier: Modifier = Modifier,
    navController: NavHostController = rememberNavController(),
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
                }
            )
        }

        composable(Routes.ONBOARDING) {
            OnboardingScreen(
                onComplete = {
                    navController.navigate(Routes.HOME) {
                        popUpTo(Routes.ONBOARDING) { inclusive = true }
                    }
                }
            )
        }

        composable(Routes.AUTH) {
            AuthScreen(
                onNavigateToLogin = {
                    navController.navigate(Routes.LOGIN)
                },
                onNavigateToRegister = {
                    navController.navigate(Routes.REGISTER)
                },
                onNavigateToOnboarding = {
                    navController.navigate(Routes.ONBOARDING) {
                        popUpTo(Routes.AUTH) { inclusive = true }
                    }
                },
            )
        }

        composable(Routes.LOGIN) {
            LoginScreen(
                onBack = { navController.popBackStack() },
                onNavigateToRegister = {
                    navController.navigate(Routes.REGISTER)
                },
                onLoginSuccess = {
                    navController.navigate(Routes.ONBOARDING) {
                        popUpTo(Routes.AUTH) { inclusive = true }
                    }
                },
            )
        }

        composable(Routes.REGISTER) {
            RegisterScreen(
                onBack = { navController.popBackStack() },
                onRegisterSuccess = {
                    navController.navigate(Routes.ONBOARDING) {
                        popUpTo(Routes.AUTH) { inclusive = true }
                    }
                },
            )
        }

        composable(Routes.HOME) {
            HomeScreen(
                onNavigateToConversation = { navController.navigate(Routes.CONVERSATION) },
                onNavigateToPeople = { navController.navigate(Routes.PEOPLE) },
                onNavigateToProfile = { navController.navigate(Routes.PROFILE) },
            )
        }

        composable(Routes.CONVERSATION) {
            ConversationScreen(
                onBack = { navController.popBackStack() },
                onNavigateToPhoto = { navController.navigate(Routes.PHOTO_PICKER) },
                onNavigateToBrief = { navController.navigate(Routes.BRIEF) },
            )
        }

        composable(Routes.PEOPLE) {
            PeopleScreen(
                onBack = { navController.popBackStack() },
            )
        }

        composable(Routes.PHOTO_PICKER) {
            PhotoPickerScreen(
                onBack = { navController.popBackStack() },
                onPhotoSelected = { navController.popBackStack() },
            )
        }

        composable(Routes.BRIEF) {
            BriefScreen(
                onBack = { navController.popBackStack() },
                onNavigateToGeneration = { navController.navigate(Routes.GENERATION) },
            )
        }

        composable(Routes.GENERATION) {
            GenerationScreen(
                onBack = { navController.popBackStack() },
                onNavigateToResult = { navController.navigate(Routes.RESULT) },
            )
        }

        composable(Routes.RESULT) {
            ResultScreen(
                onBack = { navController.popBackStack() },
                onNavigateToHome = { navController.navigate(Routes.HOME) },
            )
        }

        composable(Routes.PAYMENT) {
            PaymentScreen(
                onBack = { navController.popBackStack() },
            )
        }

        composable(Routes.PROFILE) {
            ProfileScreen(
                onBack = { navController.popBackStack() },
            )
        }
    }
}

@Composable
private fun SplashScreen(
    onNavigateToOnboarding: () -> Unit,
    onNavigateToHome: () -> Unit,
) {
}
