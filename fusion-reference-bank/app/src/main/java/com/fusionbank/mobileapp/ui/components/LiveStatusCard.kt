package com.fusionbank.mobileapp.ui.components

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.fusionbank.mobileapp.sdk.Fusion
import com.fusionbank.mobileapp.sdk.models.FusionConnectionState
import com.fusionbank.mobileapp.ui.theme.*

@Composable
fun LiveStatusCard(
    modifier: Modifier = Modifier,
    onOpenSimulator: (() -> Unit)? = null,
    onOpenTrustPassport: (() -> Unit)? = null
) {
    val context = LocalContext.current
    val connectionState by Fusion.connectionState.collectAsState()
    val activeSession by Fusion.activeSession.collectAsState()
    val trustPassport by Fusion.trustPassport.collectAsState()
    val latencyMs by Fusion.sdkLatencyMs.collectAsState()

    var logoTapCount by remember { mutableStateOf(0) }

    val (statusColor, statusText) = when (connectionState) {
        FusionConnectionState.CONNECTED -> StatusGreen to "CONNECTED"
        FusionConnectionState.SYNCING -> StatusYellow to "SYNCING"
        FusionConnectionState.DISCONNECTED -> StatusRed to "DISCONNECTED"
    }

    val sessionId = activeSession?.sessionId ?: "SDK_SESS_INACTIVE"
    val trustScore = trustPassport?.overallTrust ?: activeSession?.compositeTrustScore ?: 82.0f
    val policyVersion = trustPassport?.version ?: activeSession?.policyVersion ?: "v1.0.3"

    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(8.dp)
            .border(1.dp, CardBorderDark, RoundedCornerShape(12.dp)),
        colors = CardDefaults.cardColors(containerColor = SurfaceDark),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp)
        ) {
            // Header Row: Fusion SDK + Live Status Indicator
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.clickable {
                        logoTapCount++
                        if (logoTapCount >= 7) {
                            logoTapCount = 0
                            Toast.makeText(context, "Fusion Demo Mode Enabled", Toast.LENGTH_SHORT).show()
                            onOpenSimulator?.invoke()
                        }
                    }
                ) {
                    Icon(
                        imageVector = Icons.Default.Shield,
                        contentDescription = "Fusion Shield",
                        tint = AccentCyan,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "FUSION RISK OS — FAT-SDK v2.4.1",
                        style = MaterialTheme.typography.labelSmall,
                        color = AccentCyan,
                        fontWeight = FontWeight.Bold
                    )
                }

                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(8.dp)
                            .clip(CircleShape)
                            .background(statusColor)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = statusText,
                        style = MaterialTheme.typography.labelSmall,
                        color = statusColor,
                        fontWeight = FontWeight.Bold
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))
            Divider(color = CardBorderDark, thickness = 0.5.dp)
            Spacer(modifier = Modifier.height(8.dp))

            // Details Grid: Session, Trust Score, Policy, Latency
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text("SESSION ID", style = MaterialTheme.typography.labelSmall, color = TextSecondaryDark, fontSize = 9.sp)
                    Text(
                        text = if (sessionId.length > 16) sessionId.substring(0, 16) + "..." else sessionId,
                        style = MaterialTheme.typography.labelSmall,
                        color = TextPrimaryDark,
                        fontFamily = FontFamily.Monospace,
                        fontSize = 11.sp
                    )
                }

                Column(horizontalAlignment = Alignment.End) {
                    Text("TRUST PASSPORT", style = MaterialTheme.typography.labelSmall, color = TextSecondaryDark, fontSize = 9.sp)
                    Text(
                        text = "${String.format("%.1f", trustScore)} / 100",
                        style = MaterialTheme.typography.labelSmall,
                        color = if (trustScore >= 75) StatusGreen else if (trustScore >= 45) StatusYellow else StatusRed,
                        fontWeight = FontWeight.Bold,
                        fontSize = 11.sp
                    )
                }
            }

            Spacer(modifier = Modifier.height(6.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text("POLICY VERSION", style = MaterialTheme.typography.labelSmall, color = TextSecondaryDark, fontSize = 9.sp)
                    Text(policyVersion, style = MaterialTheme.typography.labelSmall, color = TextPrimaryDark, fontSize = 11.sp)
                }

                Column(horizontalAlignment = Alignment.End) {
                    Text("LATENCY / SYNC", style = MaterialTheme.typography.labelSmall, color = TextSecondaryDark, fontSize = 9.sp)
                    Text("${latencyMs.toInt()}ms • Live", style = MaterialTheme.typography.labelSmall, color = TextPrimaryDark, fontSize = 11.sp)
                }
            }

            if (onOpenTrustPassport != null) {
                Spacer(modifier = Modifier.height(6.dp))
                TextButton(
                    onClick = onOpenTrustPassport,
                    modifier = Modifier.align(Alignment.End)
                ) {
                    Text("View Trust Passport", color = AccentCyan, fontSize = 11.sp)
                }
            }
        }
    }
}
