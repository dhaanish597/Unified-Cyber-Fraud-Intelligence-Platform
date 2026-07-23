package com.fusionbank.mobileapp.ui.screens.transfer

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.AttachMoney
import androidx.compose.material.icons.filled.Comment
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.fusionbank.mobileapp.ui.components.LiveStatusCard
import com.fusionbank.mobileapp.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TransferScreen(
    onBack: () -> Unit,
    viewModel: TransferViewModel = hiltViewModel()
) {
    val recipient by viewModel.recipient.collectAsState()
    val amount by viewModel.amount.collectAsState()
    val remarks by viewModel.remarks.collectAsState()
    val isEvaluating by viewModel.isEvaluating.collectAsState()
    val decisionResult by viewModel.decisionResult.collectAsState()
    val errorMessage by viewModel.errorMessage.collectAsState()

    Scaffold(
        containerColor = PrimaryDark,
        topBar = {
            TopAppBar(
                title = { Text("Fund Transfer", color = TextPrimaryDark) },
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
                        Text("Instant Money Transfer", style = MaterialTheme.typography.titleMedium, color = TextPrimaryDark)
                        Spacer(modifier = Modifier.height(16.dp))

                        OutlinedTextField(
                            value = recipient,
                            onValueChange = viewModel::onRecipientChanged,
                            label = { Text("Recipient Account / ID") },
                            leadingIcon = { Icon(Icons.Default.Person, contentDescription = null, tint = AccentCyan) },
                            modifier = Modifier.fillMaxWidth()
                        )

                        Spacer(modifier = Modifier.height(12.dp))

                        OutlinedTextField(
                            value = amount,
                            onValueChange = viewModel::onAmountChanged,
                            label = { Text("Amount (INR ₹)") },
                            leadingIcon = { Icon(Icons.Default.AttachMoney, contentDescription = null, tint = AccentCyan) },
                            modifier = Modifier.fillMaxWidth()
                        )

                        Spacer(modifier = Modifier.height(12.dp))

                        OutlinedTextField(
                            value = remarks,
                            onValueChange = viewModel::onRemarksChanged,
                            label = { Text("Remarks / Purpose") },
                            leadingIcon = { Icon(Icons.Default.Comment, contentDescription = null, tint = AccentCyan) },
                            modifier = Modifier.fillMaxWidth()
                        )

                        errorMessage?.let { err ->
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(err, color = StatusRed, style = MaterialTheme.typography.bodyMedium)
                        }

                        Spacer(modifier = Modifier.height(24.dp))

                        Button(
                            onClick = { viewModel.submitTransfer() },
                            enabled = !isEvaluating,
                            modifier = Modifier.fillMaxWidth(),
                            colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue)
                        ) {
                            if (isEvaluating) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    CircularProgressIndicator(modifier = Modifier.size(18.dp), color = TextPrimaryDark, strokeWidth = 2.dp)
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text("EVALUATING FUSION RISK...")
                                }
                            } else {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Icon(Icons.Default.Shield, contentDescription = null, modifier = Modifier.size(18.dp))
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text("TRANSFER WITH FUSION VERIFICATION", fontWeight = FontWeight.Bold)
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // Decision Result Dialog
    decisionResult?.let { decision ->
        AlertDialog(
            onDismissRequest = { viewModel.dismissResult() },
            containerColor = SurfaceDark,
            title = {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    val iconColor = when (decision.decision) {
                        "ALLOW" -> StatusGreen
                        "REQUIRE_BIOMETRIC", "REQUIRE_OTP", "REQUIRE_FACE_AUTHENTICATION" -> StatusYellow
                        else -> StatusRed
                    }
                    Icon(Icons.Default.Shield, contentDescription = null, tint = iconColor, modifier = Modifier.size(28.dp))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "FUSION DECISION: ${decision.decision}",
                        style = MaterialTheme.typography.titleMedium,
                        color = iconColor,
                        fontWeight = FontWeight.Bold
                    )
                }
            },
            text = {
                Column {
                    Text("Decision ID: ${decision.decisionId}", style = MaterialTheme.typography.labelSmall, color = TextSecondaryDark)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("Confidence Score: ${decision.confidence}%", color = TextPrimaryDark, fontWeight = FontWeight.SemiBold)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("Recommended Action:", style = MaterialTheme.typography.bodyMedium, color = TextSecondaryDark)
                    Text(decision.recommendedAction, color = TextPrimaryDark)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("Reason Codes:", style = MaterialTheme.typography.labelSmall, color = TextSecondaryDark)
                    decision.reasonCodes.forEach { reason ->
                        Text("• $reason", style = MaterialTheme.typography.labelSmall, color = AccentCyan)
                    }
                }
            },
            confirmButton = {
                Button(
                    onClick = { viewModel.dismissResult() },
                    colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue)
                ) {
                    Text("ACKNOWLEDGEMENT")
                }
            }
        )
    }
}
