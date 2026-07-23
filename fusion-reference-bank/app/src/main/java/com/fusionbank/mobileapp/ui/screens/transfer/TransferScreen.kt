package com.fusionbank.mobileapp.ui.screens.transfer

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
import androidx.hilt.navigation.compose.hiltViewModel
import com.fusionbank.mobileapp.ui.components.DecisionPipelineDialog
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
                                    Text("EVALUATING FUSION PIPELINE...")
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

    // Animated Multi-Stage Decision Verification Pipeline Dialog
    DecisionPipelineDialog(
        decision = decisionResult,
        isEvaluating = isEvaluating,
        onDismiss = { viewModel.dismissResult() }
    )
}
