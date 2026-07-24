package com.fusionbank.mobileapp.ui.screens.profile

import android.os.Build
import android.widget.Toast
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.fusionbank.mobileapp.sdk.Fusion
import com.fusionbank.mobileapp.ui.components.LiveStatusCard
import com.fusionbank.mobileapp.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class, ExperimentalFoundationApi::class)
@Composable
fun ProfileScreen(
    onBack: () -> Unit,
    onLogout: () -> Unit,
    onOpenSimulator: () -> Unit,
    viewModel: ProfileViewModel = hiltViewModel()
) {
    val context = LocalContext.current
    val activeSession by Fusion.activeSession.collectAsState()
    val trustPassport by Fusion.trustPassport.collectAsState()
    val bankingProfile by Fusion.bankingProfile.collectAsState()

    val deviceId = activeSession?.deviceId ?: "DEV_UNKNOWN"
    val sessionId = activeSession?.sessionId ?: "SDK_SESS_INACTIVE"
    val trustScore = trustPassport?.compositeTrust ?: activeSession?.compositeTrustScore
    val policyVersion = activeSession?.policyVersion ?: "v1.0.3"

    val scrollState = rememberScrollState()

    Scaffold(
        containerColor = PrimaryDark,
        topBar = {
            TopAppBar(
                title = { Text("Profile & SDK Telemetry", color = TextPrimaryDark) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = TextPrimaryDark)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = PrimaryDark)
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            LiveStatusCard(onOpenSimulator = onOpenSimulator)

            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp)
                    .verticalScroll(scrollState),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Section 1: SDK Posture & Diagnostics
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Column(modifier = Modifier.padding(20.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Shield, contentDescription = null, tint = AccentCyan, modifier = Modifier.size(24.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("SDK System & Security Posture", style = MaterialTheme.typography.titleMedium, color = TextPrimaryDark)
                        }

                        Spacer(modifier = Modifier.height(16.dp))

                        ProfileDetailItem("Banking User", bankingProfile?.displayName ?: "Unavailable")
                        ProfileDetailItem("Customer ID", bankingProfile?.userId ?: "Unavailable")
                        ProfileDetailItem("Device ID", deviceId)

                        // Secret Long-Press on Version string triggers Demo Mode
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .combinedClickable(
                                    onClick = {},
                                    onLongClick = {
                                        Toast.makeText(context, "Fusion Demo Mode Enabled", Toast.LENGTH_SHORT).show()
                                        onOpenSimulator()
                                    }
                                )
                                .padding(vertical = 6.dp)
                        ) {
                            Text("SDK Version (Long Press for Demo)", style = MaterialTheme.typography.labelSmall, color = TextSecondaryDark)
                            Text(viewModel.sdkVersion, style = MaterialTheme.typography.bodyMedium, color = AccentCyan, fontWeight = FontWeight.Bold)
                            Divider(color = CardBorderDark, thickness = 0.5.dp, modifier = Modifier.padding(top = 6.dp))
                        }

                        ProfileDetailItem("Session ID", sessionId)
                        ProfileDetailItem("Trust Evidence", trustScore?.let { "${String.format("%.1f", it)} / 100" } ?: "Unavailable")
                        ProfileDetailItem("Policy Engine Version", policyVersion)
                        ProfileDetailItem("Fusion Endpoint", viewModel.endpoint)

                        Spacer(modifier = Modifier.height(16.dp))

                        Button(
                            onClick = onOpenSimulator,
                            modifier = Modifier.fillMaxWidth(),
                            colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue)
                        ) {
                            Icon(Icons.Default.BugReport, contentDescription = null, modifier = Modifier.size(18.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("OPEN CYBER ATTACK SIMULATOR", fontWeight = FontWeight.Bold)
                        }
                    }
                }

                // Section 2: Real Device Information Card
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Column(modifier = Modifier.padding(20.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Phonelink, contentDescription = null, tint = AccentCyan, modifier = Modifier.size(24.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Real Device Diagnostics", style = MaterialTheme.typography.titleMedium, color = TextPrimaryDark)
                        }
                        Spacer(modifier = Modifier.height(14.dp))

                        ProfileDetailItem("Hardware Model", "${Build.MANUFACTURER} ${Build.MODEL}")
                        ProfileDetailItem("Android Version", "Android ${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT})")
                        ProfileDetailItem("Security Patch Level", Build.VERSION.SECURITY_PATCH.takeIf { it.isNotBlank() } ?: "Unavailable")
                        ProfileDetailItem("Play Integrity Status", "NOT EVALUATED")
                    }
                }

                // Section 3: FUTURE EXPANSION PLACEHOLDERS ("COMING NEXT")
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .border(1.dp, StatusYellow.copy(alpha = 0.5f), RoundedCornerShape(16.dp)),
                    colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Column(modifier = Modifier.padding(20.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Default.AutoAwesome, contentDescription = null, tint = StatusYellow, modifier = Modifier.size(22.dp))
                                Spacer(modifier = Modifier.width(8.dp))
                                Text("COMING NEXT — ROADMAP", style = MaterialTheme.typography.titleMedium, color = StatusYellow, fontWeight = FontWeight.Bold)
                            }
                            Surface(color = StatusYellow.copy(alpha = 0.2f), shape = RoundedCornerShape(12.dp)) {
                                Text("v3.0 PRO", modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp), style = MaterialTheme.typography.labelSmall, color = StatusYellow, fontWeight = FontWeight.Bold)
                            }
                        }

                        Spacer(modifier = Modifier.height(6.dp))
                        Text("Demonstrates platform scalability for enterprise judges:", style = MaterialTheme.typography.labelSmall, color = TextSecondaryDark)
                        Spacer(modifier = Modifier.height(12.dp))

                        FuturePlaceholderItem(
                            title = "Threat Intelligence Feed",
                            subtitle = "Real-time CERT-In & MITRE ATT&CK threat vulnerability ingestion",
                            icon = Icons.Default.Security
                        )
                        FuturePlaceholderItem(
                            title = "Explainable AI (XAI Workspace)",
                            subtitle = "SHAP feature attribution & natural language counterfactual sentences",
                            icon = Icons.Default.Psychology
                        )
                        FuturePlaceholderItem(
                            title = "Decision Quality Score",
                            subtitle = "Real-time precision, recall, PR-AUC and fusion uplift benchmarking",
                            icon = Icons.Default.Assessment
                        )
                        FuturePlaceholderItem(
                            title = "Graph Explorer Visualizer",
                            subtitle = "Interactive Neo4j mule cluster graph topology & community detection",
                            icon = Icons.Default.Hub
                        )
                    }
                }

                // Section 4: Logout Button
                OutlinedButton(
                    onClick = { viewModel.logout(onLogout) },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.outlinedButtonColors(contentColor = StatusRed)
                ) {
                    Icon(Icons.Default.Logout, contentDescription = null, modifier = Modifier.size(18.dp))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("TERMINATE SESSION & LOGOUT", fontWeight = FontWeight.Bold)
                }

                Spacer(modifier = Modifier.height(16.dp))
            }
        }
    }
}

@Composable
fun FuturePlaceholderItem(
    title: String,
    subtitle: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(icon, contentDescription = null, tint = AccentCyan, modifier = Modifier.size(24.dp))
        Spacer(modifier = Modifier.width(12.dp))
        Column(modifier = Modifier.weight(1f)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(title, style = MaterialTheme.typography.bodyMedium, color = TextPrimaryDark, fontWeight = FontWeight.SemiBold, fontSize = 13.sp)
                Spacer(modifier = Modifier.width(6.dp))
                Text("SOON", style = MaterialTheme.typography.labelSmall, color = TextSecondaryDark, fontSize = 9.sp)
            }
            Text(subtitle, style = MaterialTheme.typography.labelSmall, color = TextSecondaryDark, fontSize = 11.sp)
        }
    }
    Divider(color = CardBorderDark, thickness = 0.5.dp)
}

@Composable
fun ProfileDetailItem(label: String, value: String) {
    Column(modifier = Modifier.padding(vertical = 6.dp)) {
        Text(label, style = MaterialTheme.typography.labelSmall, color = TextSecondaryDark)
        Text(value, style = MaterialTheme.typography.bodyMedium, color = TextPrimaryDark, fontWeight = FontWeight.SemiBold)
        Divider(color = CardBorderDark, thickness = 0.5.dp, modifier = Modifier.padding(top = 6.dp))
    }
}
