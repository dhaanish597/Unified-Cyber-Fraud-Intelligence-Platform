package com.fusionbank.mobileapp.ui.screens.profile

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.fusionbank.mobileapp.sdk.Fusion
import com.fusionbank.mobileapp.ui.components.LiveStatusCard
import com.fusionbank.mobileapp.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    onBack: () -> Unit,
    onLogout: () -> Unit,
    viewModel: ProfileViewModel = hiltViewModel()
) {
    val activeSession by Fusion.activeSession.collectAsState()
    val trustPassport by Fusion.trustPassport.collectAsState()

    val deviceId = activeSession?.deviceId ?: "DEV_UNKNOWN"
    val sessionId = activeSession?.sessionId ?: "SDK_SESS_INACTIVE"
    val trustScore = trustPassport?.compositeTrust ?: activeSession?.compositeTrustScore ?: 82.0f
    val policyVersion = activeSession?.policyVersion ?: "v1.0.3"

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
            LiveStatusCard()

            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp)
            ) {
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

                        ProfileDetailItem("Device ID", deviceId)
                        ProfileDetailItem("SDK Version", viewModel.sdkVersion)
                        ProfileDetailItem("Session ID", sessionId)
                        ProfileDetailItem("Trust Passport Status", "${String.format("%.1f", trustScore)} / 100")
                        ProfileDetailItem("Policy Engine Version", policyVersion)
                        ProfileDetailItem("Fusion Endpoint", viewModel.endpoint)

                        Spacer(modifier = Modifier.height(24.dp))

                        Button(
                            onClick = { viewModel.logout(onLogout) },
                            modifier = Modifier.fillMaxWidth(),
                            colors = ButtonDefaults.buttonColors(containerColor = StatusRed)
                        ) {
                            Icon(Icons.Default.Logout, contentDescription = null, modifier = Modifier.size(18.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("TERMINATE SESSION & LOGOUT", fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun ProfileDetailItem(label: String, value: String) {
    Column(modifier = Modifier.padding(vertical = 6.dp)) {
        Text(label, style = MaterialTheme.typography.labelSmall, color = TextSecondaryDark)
        Text(value, style = MaterialTheme.typography.bodyMedium, color = TextPrimaryDark, fontWeight = FontWeight.SemiBold)
        Divider(color = CardBorderDark, thickness = 0.5.dp, modifier = Modifier.padding(top = 6.dp))
    }
}
