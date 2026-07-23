package com.fusionbank.mobileapp.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.fusionbank.mobileapp.sdk.models.SDKDecisionResponse
import com.fusionbank.mobileapp.ui.theme.*
import kotlinx.coroutines.delay

data class PipelineStage(
    val id: Int,
    val name: String,
    val description: String,
    val latencyMs: Int
)

val defaultPipelineStages = listOf(
    PipelineStage(1, "Identity & Credential Attestation", "Verifying token signatures and session bounds", 12),
    PipelineStage(2, "Device Security & Integrity Check", "Scanning Play Integrity, root, and debugger state", 18),
    PipelineStage(3, "Pre-Transaction Session Intelligence", "Validating 6-checkpoint Session Trust Passport", 15),
    PipelineStage(4, "Behavioral Biometrics Analysis", "Comparing cadence, touch dynamics, and navigation speed", 22),
    PipelineStage(5, "Cyber Threat Correlation", "Correlating recent SIEM events and IP reputation", 19),
    PipelineStage(6, "Graph Mule Cluster Topology", "Traversing graph nodes for mule cluster associations", 25),
    PipelineStage(7, "Fusion Risk Engine Verdict", "Calculating composite score & final policy decision", 14)
)

@Composable
fun DecisionPipelineDialog(
    decision: SDKDecisionResponse?,
    isEvaluating: Boolean,
    onDismiss: () -> Unit
) {
    var activeStageIndex by remember { mutableStateOf(0) }
    var isPipelineFinished by remember { mutableStateOf(false) }

    LaunchedEffect(isEvaluating, decision) {
        if (isEvaluating) {
            isPipelineFinished = false
            activeStageIndex = 0
            for (i in defaultPipelineStages.indices) {
                activeStageIndex = i
                delay(220)
            }
            if (decision != null) {
                isPipelineFinished = true
            }
        } else if (decision != null) {
            activeStageIndex = defaultPipelineStages.size - 1
            isPipelineFinished = true
        }
    }

    if (isEvaluating || decision != null) {
        AlertDialog(
            onDismissRequest = { if (isPipelineFinished) onDismiss() },
            containerColor = SurfaceDark,
            title = {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.Shield, contentDescription = null, tint = AccentCyan, modifier = Modifier.size(24.dp))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = if (isPipelineFinished) "FUSION VERDICT: ${decision?.decision ?: "ALLOW"}" else "EVALUATING FUSION PIPELINE...",
                        style = MaterialTheme.typography.titleMedium,
                        color = if (isPipelineFinished) (if (decision?.decision == "ALLOW") StatusGreen else StatusRed) else TextPrimaryDark,
                        fontWeight = FontWeight.Bold
                    )
                }
            },
            text = {
                Column(modifier = Modifier.fillMaxWidth()) {
                    Text("7-Checkpoint Verification Flow", style = MaterialTheme.typography.labelSmall, color = TextSecondaryDark)
                    Spacer(modifier = Modifier.height(12.dp))

                    defaultPipelineStages.forEachIndexed { idx, stage ->
                        val isDone = idx < activeStageIndex || isPipelineFinished
                        val isCurrent = idx == activeStageIndex && !isPipelineFinished

                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 4.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            if (isDone) {
                                Icon(Icons.Default.CheckCircle, contentDescription = null, tint = StatusGreen, modifier = Modifier.size(16.dp))
                            } else if (isCurrent) {
                                CircularProgressIndicator(modifier = Modifier.size(14.dp), color = AccentCyan, strokeWidth = 2.dp)
                            } else {
                                Box(
                                    modifier = Modifier
                                        .size(14.dp)
                                        .clip(CircleShape)
                                        .background(CardBorderDark)
                                )
                            }
                            Spacer(modifier = Modifier.width(10.dp))
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = stage.name,
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = if (isDone || isCurrent) TextPrimaryDark else TextSecondaryDark,
                                    fontWeight = if (isCurrent) FontWeight.Bold else FontWeight.Normal,
                                    fontSize = 12.sp
                                )
                            }
                            Text(
                                text = "${stage.latencyMs}ms",
                                style = MaterialTheme.typography.labelSmall,
                                color = if (isDone) AccentCyan else TextSecondaryDark,
                                fontSize = 10.sp
                            )
                        }
                    }

                    if (isPipelineFinished && decision != null) {
                        Spacer(modifier = Modifier.height(14.dp))
                        Divider(color = CardBorderDark, thickness = 0.5.dp)
                        Spacer(modifier = Modifier.height(10.dp))

                        Text("Confidence Score: ${decision.confidence}%", color = TextPrimaryDark, fontWeight = FontWeight.SemiBold, fontSize = 13.sp)
                        Text("Action: ${decision.recommendedAction}", style = MaterialTheme.typography.bodyMedium, color = TextSecondaryDark, fontSize = 12.sp)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text("Reasons:", style = MaterialTheme.typography.labelSmall, color = TextSecondaryDark)
                        decision.reasonCodes.forEach { reason ->
                            Text("• $reason", style = MaterialTheme.typography.labelSmall, color = AccentCyan)
                        }
                    }
                }
            },
            confirmButton = {
                if (isPipelineFinished) {
                    Button(
                        onClick = onDismiss,
                        colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue)
                    ) {
                        Text("ACKNOWLEDGE & CONTINUE")
                    }
                }
            }
        )
    }
}
