package com.fusionbank.mobileapp.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.fusionbank.mobileapp.ui.screens.accounts.AccountsScreen
import com.fusionbank.mobileapp.ui.screens.beneficiary.BeneficiaryScreen
import com.fusionbank.mobileapp.ui.screens.bill.BillPaymentScreen
import com.fusionbank.mobileapp.ui.screens.dashboard.DashboardScreen
import com.fusionbank.mobileapp.ui.screens.login.LoginScreen
import com.fusionbank.mobileapp.ui.screens.profile.ProfileScreen
import com.fusionbank.mobileapp.ui.screens.qr.QrPaymentScreen
import com.fusionbank.mobileapp.ui.screens.splash.SplashScreen
import com.fusionbank.mobileapp.ui.screens.transfer.TransferScreen

object Destinations {
    const val SPLASH = "splash"
    const val LOGIN = "login"
    const val DASHBOARD = "dashboard"
    const val ACCOUNTS = "accounts"
    const val TRANSFER = "transfer"
    const val BENEFICIARY = "beneficiary"
    const val QR_PAYMENT = "qr_payment"
    const val BILL_PAYMENT = "bill_payment"
    const val PROFILE = "profile"
}

@Composable
fun NavGraph(
    navController: NavHostController = rememberNavController()
) {
    NavHost(
        navController = navController,
        startDestination = Destinations.SPLASH
    ) {
        composable(Destinations.SPLASH) {
            SplashScreen(
                onNavigateToLogin = {
                    navController.navigate(Destinations.LOGIN) {
                        popUpTo(Destinations.SPLASH) { inclusive = true }
                    }
                }
            )
        }

        composable(Destinations.LOGIN) {
            LoginScreen(
                onLoginSuccess = {
                    navController.navigate(Destinations.DASHBOARD) {
                        popUpTo(Destinations.LOGIN) { inclusive = true }
                    }
                }
            )
        }

        composable(Destinations.DASHBOARD) {
            DashboardScreen(
                onNavigate = { route -> navController.navigate(route) }
            )
        }

        composable(Destinations.ACCOUNTS) {
            AccountsScreen(
                onBack = { navController.popBackStack() }
            )
        }

        composable(Destinations.TRANSFER) {
            TransferScreen(
                onBack = { navController.popBackStack() }
            )
        }

        composable(Destinations.BENEFICIARY) {
            BeneficiaryScreen(
                onBack = { navController.popBackStack() }
            )
        }

        composable(Destinations.QR_PAYMENT) {
            QrPaymentScreen(
                onBack = { navController.popBackStack() }
            )
        }

        composable(Destinations.BILL_PAYMENT) {
            BillPaymentScreen(
                onBack = { navController.popBackStack() }
            )
        }

        composable(Destinations.PROFILE) {
            ProfileScreen(
                onBack = { navController.popBackStack() },
                onLogout = {
                    navController.navigate(Destinations.LOGIN) {
                        popUpTo(Destinations.DASHBOARD) { inclusive = true }
                    }
                }
            )
        }
    }
}
