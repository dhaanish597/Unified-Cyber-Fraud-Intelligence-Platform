package com.fusionbank.mobileapp.ui.screens.qr

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.fusionbank.mobileapp.ui.components.LiveStatusCard
import com.fusionbank.mobileapp.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun QrPaymentScreen(
    onBack: () -> Unit,
    viewModel: QrViewModel = hiltViewModel()
) {
    val merchant by viewModel.merchant.collectAsState()
    val amount by viewModel.amount.collectAsState()
    val isCompleted by viewModel.isCompleted.collectAsState()

    Scaffold(
        containerColor = PrimaryDark,
        topBar = {
            TopAppBar(
                title = { Text("QR Code Merchant Payment", color = TextPrimaryDark) },
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
                    Column(
                        modifier = Modifier.padding(20.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(Icons.Default.QrCodeScanner, contentDescription = null, tint = AccentCyan, modifier = Modifier.size(64.dp))
                        Spacer(modifier = Modifier.height(12.dp))
                        Text("Scan & Pay Merchant", style = MaterialTheme.typography.titleMedium, color = TextPrimaryDark)

                        Spacer(modifier = Modifier.height(16.dp))

                        OutlinedTextField(
                            value = merchant,
                            onValueChange = viewModel::onMerchantChanged,
                            label = { Text("Merchant Name / VPA") },
                            leadingIcon = { Icon(Icons.Default.Store, contentDescription = null, tint = AccentCyan) },
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

                        Spacer(modifier = Modifier.height(24.dp))

                        Button(
                            onClick = { viewModel.processQrPayment() },
                            modifier = Modifier.fillMaxWidth(),
                            colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue)
                        ) {
                            Icon(Icons.Default.Payment, contentDescription = null, modifier = Modifier.size(18.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("PAY MERCHANT WITH FUSION TELEMETRY", fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }

    if (isCompleted) {
        AlertDialog(
            onDismissRequest = { viewModel.reset(); onBack() },
            containerColor = SurfaceDark,
            title = { Text("QR Payment Successful", color = StatusGreen, fontWeight = FontWeight.Bold) },
            text = { Text("Payment processed. Telemetry event QR_PAYMENT streamed to Fusion Risk OS.", color = TextPrimaryDark) },
            confirmButton = {
                Button(onClick = { viewModel.reset(); onBack() }) {
                    Text("OK")
                }
            }
        )
    }
}
