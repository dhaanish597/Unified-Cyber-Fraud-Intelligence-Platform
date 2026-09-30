package com.fusionbank.mobileapp.ui.navigation

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.*
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.fusionbank.mobileapp.sdk.Fusion
import com.fusionbank.mobileapp.ui.screens.alerts.AlertsScreen
import com.fusionbank.mobileapp.ui.screens.crosschain.CrossChainScreen
import com.fusionbank.mobileapp.ui.screens.evidence.EvidenceScreen
import com.fusionbank.mobileapp.ui.screens.fundflow.FundFlowScreen
import com.fusionbank.mobileapp.ui.screens.home.HomeScreen
import com.fusionbank.mobileapp.ui.screens.investigations.InvestigationCenterScreen
import com.fusionbank.mobileapp.ui.screens.investigations.InvestigationListScreen
import com.fusionbank.mobileapp.ui.screens.investigations.NewInvestigationScreen
import com.fusionbank.mobileapp.ui.screens.report.ReportScreen
import com.fusionbank.mobileapp.ui.screens.risk.RiskIntelligenceScreen
import com.fusionbank.mobileapp.ui.screens.safecheck.SafeCheckScreen
import com.fusionbank.mobileapp.ui.screens.settings.ApiConfigScreen
import com.fusionbank.mobileapp.ui.screens.timeline.TimelineScreen
import com.fusionbank.mobileapp.ui.screens.transactions.TransactionLedgerScreen
import com.fusionbank.mobileapp.ui.screens.vasp.VaspAttributionScreen
import com.fusionbank.mobileapp.ui.screens.watch.WatchDetailScreen
import com.fusionbank.mobileapp.ui.screens.watch.WatchScreen
import com.fusionbank.mobileapp.ui.screens.pairing.PairingScreen
import com.fusionbank.mobileapp.ui.theme.*
import androidx.compose.ui.Alignment
import androidx.compose.material3.CircularProgressIndicator

// ─────────────────────────────────────────────────────────────────
// Route constants & helpers
// ─────────────────────────────────────────────────────────────────

object RrrDestinations {
    const val AUTH_GATE = "auth_gate"
    const val HOME = "home"
    const val INVESTIGATIONS = "investigations"
    const val NEW_INVESTIGATION = "new_investigation"
    const val ALERTS = "alerts"
    const val WATCH = "watch"
    const val SETTINGS = "settings"
    const val SAFECHECK = "safecheck"

    // Parameterised
    const val INVESTIGATION_CENTER = "investigation/{caseId}"
    const val FUND_FLOW = "investigation/{caseId}/fundflow"
    const val TRANSACTIONS = "investigation/{caseId}/transactions"
    const val RISK = "investigation/{caseId}/risk"
    const val VASP = "investigation/{caseId}/vasp"
    const val CROSS_CHAIN = "investigation/{caseId}/crosschain"
    const val EVIDENCE = "investigation/{caseId}/evidence"
    const val TIMELINE = "investigation/{caseId}/timeline"
    const val REPORT = "investigation/{caseId}/report"
    const val WATCH_DETAIL = "watch/{watchId}"

    fun investigationCenter(caseId: String) = "investigation/$caseId"
    fun fundFlow(caseId: String) = "investigation/$caseId/fundflow"
    fun transactions(caseId: String) = "investigation/$caseId/transactions"
    fun risk(caseId: String) = "investigation/$caseId/risk"
    fun vasp(caseId: String) = "investigation/$caseId/vasp"
    fun crossChain(caseId: String) = "investigation/$caseId/crosschain"
    fun evidence(caseId: String) = "investigation/$caseId/evidence"
    fun timeline(caseId: String) = "investigation/$caseId/timeline"
    fun report(caseId: String) = "investigation/$caseId/report"
    fun watchDetail(watchId: String) = "watch/$watchId"
}

// ─────────────────────────────────────────────────────────────────
// Bottom nav items (top-level tabs)
// ─────────────────────────────────────────────────────────────────

private data class NavItem(
    val route: String,
    val label: String,
    val icon: androidx.compose.ui.graphics.vector.ImageVector,
)

private val bottomNavItems = listOf(
    NavItem(RrrDestinations.HOME, "Command", Icons.Default.Dashboard),
    NavItem(RrrDestinations.INVESTIGATIONS, "Cases", Icons.Default.FolderOpen),
    NavItem(RrrDestinations.ALERTS, "Alerts", Icons.Default.NotificationsActive),
    NavItem(RrrDestinations.WATCH, "Watch", Icons.Default.Visibility),
    NavItem(RrrDestinations.SAFECHECK, "SafeCheck", Icons.Default.QrCodeScanner),
    NavItem(RrrDestinations.SETTINGS, "Config", Icons.Default.Settings),
)

private val topLevelRoutes = bottomNavItems.map { it.route }.toSet()

// ─────────────────────────────────────────────────────────────────
// NavGraph
// ─────────────────────────────────────────────────────────────────

@Composable
fun NavGraph(navController: NavHostController = rememberNavController()) {
    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = backStackEntry?.destination?.route

    var previousRoute by remember { mutableStateOf<String?>(null) }
    LaunchedEffect(currentRoute) {
        currentRoute?.let { route ->
            previousRoute?.let { Fusion.reportLifecycleEvent("SCREEN_CLOSE") }
            Fusion.reportLifecycleEvent("SCREEN_OPEN")
            previousRoute = route
        }
    }

    val showBottomBar = currentRoute in topLevelRoutes

    Scaffold(
        containerColor = RrrBackground,
        bottomBar = {
            if (showBottomBar) {
                NavigationBar(containerColor = RrrSurface, tonalElevation = 0.dp) {
                    bottomNavItems.forEach { item ->
                        NavigationBarItem(
                            selected = currentRoute == item.route,
                            onClick = {
                                if (currentRoute != item.route) {
                                    navController.navigate(item.route) {
                                        popUpTo(RrrDestinations.HOME) { saveState = true }
                                        launchSingleTop = true
                                        restoreState = true
                                    }
                                }
                            },
                            icon = { Icon(item.icon, contentDescription = item.label) },
                            label = { Text(item.label, fontSize = 10.sp, fontWeight = if (currentRoute == item.route) FontWeight.Bold else FontWeight.Normal) },
                            colors = NavigationBarItemDefaults.colors(
                                selectedIconColor = RrrCyan,
                                selectedTextColor = RrrCyan,
                                unselectedIconColor = RrrTextMuted,
                                unselectedTextColor = RrrTextMuted,
                                indicatorColor = RrrCyan.copy(alpha = 0.12f),
                            ),
                        )
                    }
                }
            }
        },
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = RrrDestinations.AUTH_GATE,
            modifier = Modifier.padding(innerPadding).background(RrrBackground),
        ) {

            composable(RrrDestinations.AUTH_GATE) {
                AuthGate(
                    onAuthenticated = {
                        navController.navigate(RrrDestinations.HOME) {
                            popUpTo(RrrDestinations.AUTH_GATE) { inclusive = true }
                        }
                    },
                )
            }

            // ── Top-level tabs ────────────────────────────────────────
            composable(RrrDestinations.HOME) {
                HomeScreen(onNavigate = { navController.navigate(it) })
            }

            composable(RrrDestinations.INVESTIGATIONS) {
                InvestigationListScreen(onNavigate = { navController.navigate(it) })
            }

            composable(RrrDestinations.ALERTS) {
                AlertsScreen(onNavigate = { navController.navigate(it) })
            }

            composable(RrrDestinations.WATCH) {
                WatchScreen(onNavigate = { navController.navigate(it) })
            }

            composable(RrrDestinations.SETTINGS) {
                ApiConfigScreen(onBack = { navController.popBackStack() })
            }

            composable(RrrDestinations.SAFECHECK) {
                SafeCheckScreen()
            }

            // ── New investigation ─────────────────────────────────────
            composable(RrrDestinations.NEW_INVESTIGATION) {
                NewInvestigationScreen(
                    onBack = { navController.popBackStack() },
                    onInvestigationCreated = { caseId ->
                        navController.navigate(RrrDestinations.investigationCenter(caseId)) {
                            popUpTo(RrrDestinations.NEW_INVESTIGATION) { inclusive = true }
                        }
                    },
                )
            }

            // ── Investigation center ──────────────────────────────────
            composable(
                RrrDestinations.INVESTIGATION_CENTER,
                arguments = listOf(navArgument("caseId") { type = NavType.StringType }),
            ) { backStack ->
                val caseId = backStack.arguments?.getString("caseId") ?: return@composable
                InvestigationCenterScreen(
                    caseId = caseId,
                    onBack = { navController.popBackStack() },
                    onNavigate = { navController.navigate(it) },
                )
            }

            // ── Fund flow ─────────────────────────────────────────────
            composable(
                RrrDestinations.FUND_FLOW,
                arguments = listOf(navArgument("caseId") { type = NavType.StringType }),
            ) { backStack ->
                val caseId = backStack.arguments?.getString("caseId") ?: return@composable
                FundFlowScreen(caseId = caseId, onBack = { navController.popBackStack() })
            }

            // ── Transaction ledger ────────────────────────────────────
            composable(
                RrrDestinations.TRANSACTIONS,
                arguments = listOf(navArgument("caseId") { type = NavType.StringType }),
            ) { backStack ->
                val caseId = backStack.arguments?.getString("caseId") ?: return@composable
                TransactionLedgerScreen(caseId = caseId, onBack = { navController.popBackStack() })
            }

            // ── Risk intelligence ─────────────────────────────────────
            composable(
                RrrDestinations.RISK,
                arguments = listOf(navArgument("caseId") { type = NavType.StringType }),
            ) { backStack ->
                val caseId = backStack.arguments?.getString("caseId") ?: return@composable
                RiskIntelligenceScreen(caseId = caseId, onBack = { navController.popBackStack() })
            }

            // ── VASP attribution ──────────────────────────────────────
            composable(
                RrrDestinations.VASP,
                arguments = listOf(navArgument("caseId") { type = NavType.StringType }),
            ) { backStack ->
                val caseId = backStack.arguments?.getString("caseId") ?: return@composable
                VaspAttributionScreen(caseId = caseId, onBack = { navController.popBackStack() })
            }

            // ── Cross-chain ───────────────────────────────────────────
            composable(
                RrrDestinations.CROSS_CHAIN,
                arguments = listOf(navArgument("caseId") { type = NavType.StringType }),
            ) { backStack ->
                val caseId = backStack.arguments?.getString("caseId") ?: return@composable
                CrossChainScreen(caseId = caseId, onBack = { navController.popBackStack() })
            }

            // ── Evidence ─────────────────────────────────────────────
            composable(
                RrrDestinations.EVIDENCE,
                arguments = listOf(navArgument("caseId") { type = NavType.StringType }),
            ) { backStack ->
                val caseId = backStack.arguments?.getString("caseId") ?: return@composable
                EvidenceScreen(caseId = caseId, onBack = { navController.popBackStack() })
            }

            // ── Timeline ──────────────────────────────────────────────
            composable(
                RrrDestinations.TIMELINE,
                arguments = listOf(navArgument("caseId") { type = NavType.StringType }),
            ) { backStack ->
                val caseId = backStack.arguments?.getString("caseId") ?: return@composable
                TimelineScreen(caseId = caseId, onBack = { navController.popBackStack() })
            }

            // ── Report ────────────────────────────────────────────────
            composable(
                RrrDestinations.REPORT,
                arguments = listOf(navArgument("caseId") { type = NavType.StringType }),
            ) { backStack ->
                val caseId = backStack.arguments?.getString("caseId") ?: return@composable
                ReportScreen(caseId = caseId, onBack = { navController.popBackStack() })
            }

            // ── Watch detail ──────────────────────────────────────────
            composable(
                RrrDestinations.WATCH_DETAIL,
                arguments = listOf(navArgument("watchId") { type = NavType.StringType }),
            ) { backStack ->
                val watchId = backStack.arguments?.getString("watchId") ?: return@composable
                WatchDetailScreen(watchId = watchId, onBack = { navController.popBackStack() })
            }
        }
    }
}

@Composable
private fun AuthGate(onAuthenticated: () -> Unit) {
    var resolving by remember { mutableStateOf(true) }
    var paired by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        Fusion.restorePairedSession { result ->
            resolving = false
            paired = result.isSuccess
        }
    }

    when {
        resolving -> Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator(color = RrrCyan)
        }
        paired -> LaunchedEffect(Unit) { onAuthenticated() }
        else -> PairingScreen(onPaired = onAuthenticated)
    }
}
