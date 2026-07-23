package com.fusionbank.mobileapp.ui.screens.bill

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
fun BillPaymentScreen(
    onBack: () -> Unit,
    viewModel: BillViewModel = hiltViewModel()
) {
    val category by viewModel.category.collectAsState()
    val amount by viewModel.amount.collectAsState()
    val isCompleted by viewModel.isCompleted.collectAsState()

    Scaffold(
        containerColor = PrimaryDark,
        topBar = {
            TopAppBar(
                title = { Text("Utility Bill Payment", color = TextPrimaryDark) },
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
                        Text("Pay Utility & Mobile Bills", style = MaterialTheme.typography.titleMedium, color = TextPrimaryDark)
                        Spacer(modifier = Modifier.height(16.dp))

                        OutlinedTextField(
                            value = category,
                            onValueChange = viewModel::onCategoryChanged,
                            label = { Text("Category (e.g. Electricity, Water, Mobile)") },
                            leadingIcon = { Icon(Icons.Default.Receipt, contentDescription = null, tint = AccentCyan) },
                            modifier = Modifier.fillMaxWidth()
                        )

                        Spacer(modifier = Modifier.height(12.dp))

                        OutlinedTextField(
                            value = amount,
                            onValueChange = viewModel::onAmountChanged,
                            label = { Text("Bill Amount (INR ₹)") },
                            leadingIcon = { Icon(Icons.Default.AttachMoney, contentDescription = null, tint = AccentCyan) },
                            modifier = Modifier.fillMaxWidth()
                        )

                        Spacer(modifier = Modifier.height(24.dp))

                        Button(
                            onClick = { viewModel.processBillPayment() },
                            modifier = Modifier.fillMaxWidth(),
                            colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue)
                        ) {
                            Icon(Icons.Default.CheckCircle, contentDescription = null, modifier = Modifier.size(18.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("PAY BILL WITH FUSION TELEMETRY", fontWeight = FontWeight.Bold)
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
            title = { Text("Bill Payment Complete", color = StatusGreen, fontWeight = FontWeight.Bold) },
            text = { Text("Bill payment successful. Telemetry event BILL_PAYMENT streamed to Fusion Risk OS.", color = TextPrimaryDark) },
            confirmButton = {
                Button(onClick = { viewModel.reset(); onBack() }) {
                    Text("OK")
                }
            }
        )
    }
}
