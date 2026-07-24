package com.fusionbank.mobileapp.ui.screens.trust

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Divider
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.fusionbank.mobileapp.sdk.Fusion
import com.fusionbank.mobileapp.sdk.models.FusionConnectionState
import com.fusionbank.mobileapp.sdk.models.SDKTrustComponent
import com.fusionbank.mobileapp.ui.theme.AccentCyan
import com.fusionbank.mobileapp.ui.theme.CardBorderDark
import com.fusionbank.mobileapp.ui.theme.PrimaryDark
import com.fusionbank.mobileapp.ui.theme.StatusGreen
import com.fusionbank.mobileapp.ui.theme.StatusRed
import com.fusionbank.mobileapp.ui.theme.StatusYellow
import com.fusionbank.mobileapp.ui.theme.SurfaceDark
import com.fusionbank.mobileapp.ui.theme.TextPrimaryDark
import com.fusionbank.mobileapp.ui.theme.TextSecondaryDark

private val componentOrder = listOf(
    "identity", "device", "runtime", "behaviour", "network",
    "geo", "threat", "graph", "transaction"
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TrustPassportScreen(onBack: () -> Unit) {
    val passport by Fusion.trustPassport.collectAsState()
    val history by Fusion.trustHistory.collectAsState()
    val deltas by Fusion.trustDeltas.collectAsState()
    val connection by Fusion.connectionState.collectAsState()
    val latency by Fusion.sdkLatencyMs.collectAsState()

    LaunchedEffect(Unit) {
        Fusion.getTrustPassport { }
        Fusion.refreshTrustHistory()
    }

    Scaffold(
        containerColor = PrimaryDark,
        topBar = {
            TopAppBar(
                title = { Text("Trust Passport", color = TextPrimaryDark) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = TextPrimaryDark)
                    }
                },
                actions = {
                    IconButton(onClick = {
                        Fusion.getTrustPassport { }
                        Fusion.refreshTrustHistory()
                    }) {
                        Icon(Icons.Default.Refresh, contentDescription = "Refresh", tint = AccentCyan)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = SurfaceDark)
            )
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            item {
                PassportSummary(
                    score = passport?.overallTrust,
                    confidence = passport?.confidence,
                    status = passport?.currentStatus,
                    trend = passport?.trustTrend,
                    updatedAt = passport?.updatedTime,
                    latency = latency,
                    connection = connection
                )
            }

            item {
                Text(
                    "TRUST COMPONENTS",
                    color = TextSecondaryDark,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold
                )
            }

            if (passport == null) {
                item { EmptyCard("Waiting for the live Trust Passport stream.") }
            } else {
                items(componentOrder) { name ->
                    val component = passport?.components?.get(name)
                    ComponentRow(name, component)
                }
            }

            item {
                Text(
                    "RECENT TRUST DELTAS",
                    color = TextSecondaryDark,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold
                )
            }
            if (deltas.isEmpty()) {
                item { EmptyCard("No component changes have been recorded.") }
            } else {
                items(deltas.take(12), key = { it.deltaId }) { delta ->
                    Card(
                        colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Column(Modifier.fillMaxWidth().padding(12.dp)) {
                            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                Text(delta.component.uppercase(), color = TextPrimaryDark, fontWeight = FontWeight.Bold, fontSize = 11.sp)
                                Text(
                                    "${if (delta.difference > 0) "+" else ""}${"%.1f".format(delta.difference)}",
                                    color = trustColor(delta.currentTrust),
                                    fontWeight = FontWeight.Bold
                                )
                            }
                            Text(
                                "${"%.1f".format(delta.previousTrust)} → ${"%.1f".format(delta.currentTrust)}",
                                color = TextSecondaryDark,
                                fontFamily = FontFamily.Monospace,
                                fontSize = 11.sp
                            )
                            Text(delta.reason, color = TextSecondaryDark, fontSize = 11.sp)
                        }
                    }
                }
            }

            item {
                Text(
                    "TRUST HISTORY",
                    color = TextSecondaryDark,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold
                )
            }
            if (history.isEmpty()) {
                item { EmptyCard("History will populate as session events arrive.") }
            } else {
                items(history.takeLast(20).reversed(), key = { it.snapshotId }) { snapshot ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(SurfaceDark, RoundedCornerShape(10.dp))
                            .padding(12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(Modifier.weight(1f)) {
                            Text(snapshot.eventType, color = TextPrimaryDark, fontWeight = FontWeight.SemiBold, fontSize = 11.sp)
                            Text(snapshot.reason, color = TextSecondaryDark, fontSize = 10.sp, maxLines = 1)
                        }
                        Text(
                            "${"%.1f".format(snapshot.currentTrust)} (${if (snapshot.delta > 0) "+" else ""}${"%.1f".format(snapshot.delta)})",
                            color = trustColor(snapshot.currentTrust),
                            fontFamily = FontFamily.Monospace,
                            fontSize = 11.sp
                        )
                    }
                }
            }
            item { Spacer(Modifier.height(20.dp)) }
        }
    }
}

@Composable
private fun PassportSummary(
    score: Float?,
    confidence: Float?,
    status: String?,
    trend: String?,
    updatedAt: String?,
    latency: Float,
    connection: FusionConnectionState
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = SurfaceDark),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            Modifier.fillMaxWidth().padding(18.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(Icons.Default.Shield, contentDescription = null, tint = AccentCyan, modifier = Modifier.size(30.dp))
            Spacer(Modifier.height(8.dp))
            Text(
                score?.let { "%.1f".format(it) } ?: "—",
                color = score?.let(::trustColor) ?: TextSecondaryDark,
                fontSize = 42.sp,
                fontWeight = FontWeight.Black
            )
            Text("OVERALL TRUST", color = TextSecondaryDark, fontSize = 10.sp)
            Spacer(Modifier.height(12.dp))
            Divider(color = CardBorderDark)
            Spacer(Modifier.height(12.dp))
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                SummaryValue("STATUS", status ?: "WAITING")
                SummaryValue("CONFIDENCE", confidence?.let { "${"%.0f".format(it)}%" } ?: "—")
                SummaryValue("TREND", trend ?: "—")
            }
            Spacer(Modifier.height(12.dp))
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("Stream: $connection", color = if (connection == FusionConnectionState.CONNECTED) StatusGreen else StatusYellow, fontSize = 10.sp)
                Text("${latency.toInt()} ms", color = TextSecondaryDark, fontSize = 10.sp)
            }
            if (!updatedAt.isNullOrBlank()) {
                Text("Updated $updatedAt", color = TextSecondaryDark, fontSize = 9.sp, maxLines = 1)
            }
        }
    }
}

@Composable
private fun SummaryValue(label: String, value: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(label, color = TextSecondaryDark, fontSize = 9.sp)
        Text(value, color = TextPrimaryDark, fontSize = 11.sp, fontWeight = FontWeight.Bold)
    }
}

@Composable
private fun ComponentRow(name: String, component: SDKTrustComponent?) {
    val value = component?.value ?: 0f
    Card(
        colors = CardDefaults.cardColors(containerColor = SurfaceDark),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(Modifier.fillMaxWidth().padding(12.dp)) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text(name.uppercase(), color = TextPrimaryDark, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                Text(
                    component?.let { "${"%.1f".format(value)}  ${if (it.difference > 0) "+" else ""}${"%.1f".format(it.difference)}" } ?: "—",
                    color = if (component == null) TextSecondaryDark else trustColor(value),
                    fontFamily = FontFamily.Monospace,
                    fontSize = 11.sp
                )
            }
            Spacer(Modifier.height(7.dp))
            LinearProgressIndicator(
                progress = value / 100f,
                modifier = Modifier.fillMaxWidth().height(5.dp).clip(CircleShape),
                color = trustColor(value),
                trackColor = PrimaryDark
            )
            Spacer(Modifier.height(5.dp))
            Text(
                component?.let { "${it.trend} • ${"%.0f".format(it.confidence)}% confidence" } ?: "Awaiting evidence",
                color = TextSecondaryDark,
                fontSize = 9.sp
            )
        }
    }
}

@Composable
private fun EmptyCard(message: String) {
    Box(
        modifier = Modifier.fillMaxWidth().background(SurfaceDark, RoundedCornerShape(12.dp)).padding(24.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(message, color = TextSecondaryDark, fontSize = 12.sp)
    }
}

private fun trustColor(score: Float): Color = when {
    score >= 85f -> StatusGreen
    score >= 70f -> StatusYellow
    else -> StatusRed
}
