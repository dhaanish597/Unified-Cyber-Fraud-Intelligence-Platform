package com.fusionbank.mobileapp.ui.screens.simulator

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.fusionbank.mobileapp.sdk.Fusion
import com.fusionbank.mobileapp.sdk.models.FusionConnectionState
import com.fusionbank.mobileapp.ui.components.LiveStatusCard
import com.fusionbank.mobileapp.ui.theme.*
import kotlinx.coroutines.flow.MutableStateFlow

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SimulatorScreen(
    onBack: () -> Unit,
    viewModel: SimulatorViewModel = hiltViewModel()
) {
    val connectionState by Fusion.connectionState.collectAsState()
    val activeSession by Fusion.activeSession.collectAsState()
    val trustPassport by Fusion.trustPassport.collectAsState()
    val latestDecision by viewModel.latestDecision.collectAsState()
    val eventLogs by viewModel.eventLogs.collectAsState()
    val developerLogs by viewModel.developerLogs.collectAsState()
    val isCampaignRunning by viewModel.isCampaignRunning.collectAsState()

    var showDevLogs by remember { mutableStateOf(false) }

    Scaffold(
        containerColor = PrimaryDark,
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.BugReport, contentDescription = null, tint = StatusRed, modifier = Modifier.size(24.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("CYBER ATTACK SIMULATOR", color = TextPrimaryDark, fontWeight = FontWeight.Bold)
                    }
                },
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

            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 14.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                // Section 11: 1-Click Threat Campaigns & Scenario Library (PROMINENT TOP)
                item {
                    SimulatorCard(title = "11. Threat Campaign Library (1-Click Demonstrations)", icon = Icons.Default.FlashOn, iconTint = StatusYellow) {
                        Text(
                            "Trigger realistic multi-stage cyber campaigns that flow through Fusion Risk OS:",
                            style = MaterialTheme.typography.labelSmall,
                            color = TextSecondaryDark
                        )
                        Spacer(modifier = Modifier.height(10.dp))

                        DemoScenarioLibrary.scenarios.chunked(2).forEach { pair ->
                            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                pair.forEach { scenario ->
                                    Button(
                                        onClick = { viewModel.runScenario(scenario) },
                                        enabled = !isCampaignRunning,
                                        modifier = Modifier.weight(1f),
                                        colors = ButtonDefaults.buttonColors(
                                            containerColor = if (scenario.threatLevel == "CRITICAL") StatusRed else if (scenario.threatLevel == "HIGH") StatusYellow else PrimaryBlue
                                        ),
                                        shape = RoundedCornerShape(8.dp)
                                    ) {
                                        Text(scenario.title, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                                    }
                                }
                            }
                            Spacer(modifier = Modifier.height(6.dp))
                        }
                    }
                }

                // Section 13: Trust Passport Preview
                item {
                    val tp = trustPassport
                    SimulatorCard(title = "13. Realtime Trust Passport Breakdown", icon = Icons.Default.Shield, iconTint = AccentCyan) {
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            ScoreMetric("IDENTITY", tp?.compositeTrust ?: 82.0f)
                            ScoreMetric("DEVICE", tp?.deviceTrust ?: 88.0f)
                            ScoreMetric("RUNTIME", tp?.runtimeTrust ?: 94.0f)
                            ScoreMetric("BEHAVIOUR", tp?.behaviourTrust ?: 79.0f)
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            ScoreMetric("NETWORK", tp?.networkTrust ?: 91.0f)
                            ScoreMetric("SESSION", tp?.sessionTrust ?: 85.0f)
                            ScoreMetric("OVERALL", tp?.compositeTrust ?: 82.0f)
                        }
                    }
                }

                // Section 14: Decision Engine Preview
                item {
                    val dec = latestDecision
                    SimulatorCard(title = "14. Decision Engine Live Verdict", icon = Icons.Default.Gavel, iconTint = AccentCyan) {
                        if (dec == null) {
                            Text("No decision requested yet. Trigger a transfer or transaction simulation below.", style = MaterialTheme.typography.bodyMedium, color = TextSecondaryDark)
                        } else {
                            val color = when (dec.decision) {
                                "ALLOW" -> StatusGreen
                                "REQUIRE_BIOMETRIC", "REQUIRE_OTP" -> StatusYellow
                                else -> StatusRed
                            }
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Box(modifier = Modifier.size(10.dp).clip(CircleShape).background(color))
                                Spacer(modifier = Modifier.width(6.dp))
                                Text("VERDICT: ${dec.decision}", style = MaterialTheme.typography.titleMedium, color = color, fontWeight = FontWeight.Bold)
                            }
                            Text("Confidence: ${dec.confidence}% • Latency: ${dec.decisionLatencyMs}ms", style = MaterialTheme.typography.labelSmall, color = TextSecondaryDark)
                            Text("Recommended: ${dec.recommendedAction}", style = MaterialTheme.typography.bodyMedium, color = TextPrimaryDark)
                            Text("Reasons: ${dec.reasonCodes.joinToString()}", style = MaterialTheme.typography.labelSmall, color = AccentCyan)
                        }
                    }
                }

                // Section 2: Device Security
                item {
                    SimulatorCard(title = "2. Device Security Telemetry", icon = Icons.Default.PhonelinkLock) {
                        ToggleRow("Rooted Device (su binary)", viewModel.rootDetected) { viewModel.triggerEvent(if (it) "ROOT_DETECTED" else "ROOT_CLEARED") }
                        ToggleRow("Magisk Framework", viewModel.magiskDetected) { viewModel.triggerEvent("MAGISK_DETECTED") }
                        ToggleRow("Bootloader Unlocked", viewModel.bootloaderUnlocked) { viewModel.triggerEvent("BOOTLOADER_UNLOCKED") }
                        ToggleRow("USB Debugging Enabled", viewModel.usbDebugging) { viewModel.triggerEvent("USB_DEBUGGING_ON") }
                        ToggleRow("Developer Options Enabled", viewModel.devOptions) { viewModel.triggerEvent("DEV_OPTIONS_ON") }
                        ToggleRow("Emulator (x86 Android)", viewModel.emulatorDetected) { viewModel.triggerEvent("EMULATOR_DETECTED") }
                    }
                }

                // Section 3: Runtime Integrity
                item {
                    SimulatorCard(title = "3. Runtime Integrity & Tampering", icon = Icons.Default.Memory) {
                        ToggleRow("Debugger Attached", viewModel.debuggerAttached) { viewModel.triggerEvent("DEBUGGER_ATTACHED") }
                        ToggleRow("Frida Instrumentation", viewModel.fridaDetected) { viewModel.triggerEvent("FRIDA_DETECTED") }
                        ToggleRow("Xposed Framework", viewModel.xposedDetected) { viewModel.triggerEvent("XPOSED_DETECTED") }
                        ToggleRow("Runtime Code Hooking", viewModel.runtimeHooking) { viewModel.triggerEvent("RUNTIME_HOOKING") }
                        ToggleRow("Memory Tampering", viewModel.memoryTampering) { viewModel.triggerEvent("MEMORY_TAMPERING") }
                        ToggleRow("Cert Pinning Failure", viewModel.certPinningFailure) { viewModel.triggerEvent("CERT_PINNING_FAILURE") }
                    }
                }

                // Section 4: Overlay & Screen Threats
                item {
                    SimulatorCard(title = "4. Overlay & Display Attacks", icon = Icons.Default.Layers) {
                        ToggleRow("Malicious Window Overlay", viewModel.overlayAttack) { viewModel.triggerEvent("OVERLAY_DETECTED") }
                        ToggleRow("Accessibility Service Abuse", viewModel.accessibilityAbuse) { viewModel.triggerEvent("ACCESSIBILITY_ABUSE") }
                        ToggleRow("Screen Recording Active", viewModel.screenRecording) { viewModel.triggerEvent("SCREEN_RECORDING") }
                        ToggleRow("Tap Injection Attack", viewModel.tapInjection) { viewModel.triggerEvent("TAP_INJECTION") }
                    }
                }

                // Section 5: Network Threats
                item {
                    SimulatorCard(title = "5. Network Threats & Proxies", icon = Icons.Default.Router) {
                        ToggleRow("VPN Tunnel Active", viewModel.vpnEnabled) { viewModel.triggerEvent("VPN_ENABLED") }
                        ToggleRow("TOR Anonymizer Node", viewModel.torEnabled) { viewModel.triggerEvent("TOR_NODE_DETECTED") }
                        ToggleRow("HTTP/SOCKS Proxy", viewModel.proxyEnabled) { viewModel.triggerEvent("PROXY_DETECTED") }
                        ToggleRow("Public Unsecured Wi-Fi", viewModel.publicWifi) { viewModel.triggerEvent("PUBLIC_WIFI") }
                    }
                }

                // Section 6: Session Attacks
                item {
                    SimulatorCard(title = "6. Session Attack Triggers", icon = Icons.Default.VpnKey) {
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            TriggerButton("Session Hijack", Modifier.weight(1f)) { viewModel.triggerEvent("SESSION_HIJACK_ATTEMPT") }
                            TriggerButton("Concurrent Login", Modifier.weight(1f)) { viewModel.triggerEvent("CONCURRENT_LOGIN") }
                        }
                        Spacer(modifier = Modifier.height(6.dp))
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            TriggerButton("Session Replay", Modifier.weight(1f)) { viewModel.triggerEvent("SESSION_REPLAY") }
                            TriggerButton("Cookie Theft", Modifier.weight(1f)) { viewModel.triggerEvent("COOKIE_THEFT") }
                        }
                    }
                }

                // Section 8 & 9: Location & Fingerprint
                item {
                    SimulatorCard(title = "8 & 9. Location & Fingerprint Intelligence", icon = Icons.Default.LocationOn) {
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            TriggerButton("Impossible Travel", Modifier.weight(1f)) { viewModel.triggerEvent("IMPOSSIBLE_TRAVEL") }
                            TriggerButton("GPS Spoofing", Modifier.weight(1f)) { viewModel.triggerEvent("GPS_SPOOFED") }
                        }
                        Spacer(modifier = Modifier.height(6.dp))
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            TriggerButton("New Device", Modifier.weight(1f)) { viewModel.triggerEvent("NEW_DEVICE_DETECTED") }
                            TriggerButton("SIM Swapped", Modifier.weight(1f)) { viewModel.triggerEvent("SIM_CARD_CHANGED") }
                        }
                    }
                }

                // Section 10: Transaction Simulator
                item {
                    SimulatorCard(title = "10. Transaction Decision Simulator", icon = Icons.Default.AttachMoney) {
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                            TriggerButton("₹500", Modifier.weight(1f)) { viewModel.triggerDecision("TRANSFER", 500.0) }
                            TriggerButton("₹5,000", Modifier.weight(1f)) { viewModel.triggerDecision("TRANSFER", 5000.0) }
                            TriggerButton("₹50,000", Modifier.weight(1f)) { viewModel.triggerDecision("TRANSFER", 50000.0) }
                            TriggerButton("₹5,00,000", Modifier.weight(1f)) { viewModel.triggerDecision("TRANSFER", 500000.0) }
                        }
                    }
                }

                // Section 12: Live Event Stream
                item {
                    SimulatorCard(title = "12. Live Event Stream Log", icon = Icons.Default.List) {
                        Column(modifier = Modifier.heightIn(max = 200.dp)) {
                            eventLogs.take(15).forEach { log ->
                                Row(
                                    modifier = Modifier.fillMaxWidth().padding(vertical = 3.dp),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Text("${log.timestamp} • ${log.eventName}", style = MaterialTheme.typography.labelSmall, color = TextPrimaryDark)
                                    Text("${log.status} (${log.latencyMs}ms)", style = MaterialTheme.typography.labelSmall, color = AccentCyan)
                                }
                                Divider(color = CardBorderDark, thickness = 0.5.dp)
                            }
                        }
                    }
                }

                // Section 15: Developer Logs
                item {
                    SimulatorCard(title = "15. Developer SDK Logs", icon = Icons.Default.Code) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text("Raw REST & WebSocket payloads", style = MaterialTheme.typography.labelSmall, color = TextSecondaryDark)
                            TextButton(onClick = { showDevLogs = !showDevLogs }) {
                                Text(if (showDevLogs) "Hide" else "Show Logs", color = AccentCyan)
                            }
                        }

                        AnimatedVisibility(visible = showDevLogs) {
                            Column(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .background(Color.Black, RoundedCornerShape(8.dp))
                                    .padding(8.dp)
                                    .heightIn(max = 200.dp)
                            ) {
                                developerLogs.take(20).forEach { line ->
                                    Text(line, style = MaterialTheme.typography.labelSmall, color = StatusGreen, fontFamily = FontFamily.Monospace, fontSize = 10.sp)
                                }
                            }
                        }
                    }
                }

                item { Spacer(modifier = Modifier.height(24.dp)) }
            }
        }
    }
}

@Composable
fun SimulatorCard(
    title: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    iconTint: Color = AccentCyan,
    content: @Composable ColumnScope.() -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, CardBorderDark, RoundedCornerShape(12.dp)),
        colors = CardDefaults.cardColors(containerColor = SurfaceDark),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(icon, contentDescription = null, tint = iconTint, modifier = Modifier.size(20.dp))
                Spacer(modifier = Modifier.width(8.dp))
                Text(title, style = MaterialTheme.typography.titleMedium, color = TextPrimaryDark, fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
            }
            Spacer(modifier = Modifier.height(10.dp))
            content()
        }
    }
}

@Composable
fun ToggleRow(
    label: String,
    state: MutableStateFlow<Boolean>,
    onToggle: (Boolean) -> Unit
) {
    val isChecked by state.collectAsState()
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 2.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(label, style = MaterialTheme.typography.bodyMedium, color = TextPrimaryDark, fontSize = 13.sp)
        Switch(
            checked = isChecked,
            onCheckedChange = {
                state.value = it
                onToggle(it)
            },
            colors = SwitchDefaults.colors(checkedThumbColor = PrimaryBlue, checkedTrackColor = AccentCyan)
        )
    }
}

@Composable
fun TriggerButton(
    label: String,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    OutlinedButton(
        onClick = onClick,
        modifier = modifier,
        shape = RoundedCornerShape(8.dp),
        colors = ButtonDefaults.outlinedButtonColors(contentColor = TextPrimaryDark)
    ) {
        Text(label, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
    }
}

@Composable
fun ScoreMetric(label: String, score: Float) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(label, style = MaterialTheme.typography.labelSmall, color = TextSecondaryDark, fontSize = 9.sp)
        Text(
            "${score.toInt()}",
            style = MaterialTheme.typography.titleMedium,
            color = if (score >= 75) StatusGreen else if (score >= 45) StatusYellow else StatusRed,
            fontWeight = FontWeight.Bold
        )
    }
}
