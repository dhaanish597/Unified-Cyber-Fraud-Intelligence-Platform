package com.fusionbank.mobileapp.ui.screens.beneficiary

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
fun BeneficiaryScreen(
    onBack: () -> Unit,
    viewModel: BeneficiaryViewModel = hiltViewModel()
) {
    val name by viewModel.name.collectAsState()
    val account by viewModel.account.collectAsState()
    val ifsc by viewModel.ifsc.collectAsState()
    val isSaved by viewModel.isSaved.collectAsState()

    Scaffold(
        containerColor = PrimaryDark,
        topBar = {
            TopAppBar(
                title = { Text("Add New Beneficiary", color = TextPrimaryDark) },
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
                        Text("Payee Details", style = MaterialTheme.typography.titleMedium, color = TextPrimaryDark)
                        Spacer(modifier = Modifier.height(16.dp))

                        OutlinedTextField(
                            value = name,
                            onValueChange = viewModel::onNameChanged,
                            label = { Text("Payee Full Name") },
                            leadingIcon = { Icon(Icons.Default.Person, contentDescription = null, tint = AccentCyan) },
                            modifier = Modifier.fillMaxWidth()
                        )

                        Spacer(modifier = Modifier.height(12.dp))

                        OutlinedTextField(
                            value = account,
                            onValueChange = viewModel::onAccountChanged,
                            label = { Text("Bank Account Number") },
                            leadingIcon = { Icon(Icons.Default.AccountBalance, contentDescription = null, tint = AccentCyan) },
                            modifier = Modifier.fillMaxWidth()
                        )

                        Spacer(modifier = Modifier.height(12.dp))

                        OutlinedTextField(
                            value = ifsc,
                            onValueChange = viewModel::onIfscChanged,
                            label = { Text("IFSC Code (e.g. MAHB0001029)") },
                            leadingIcon = { Icon(Icons.Default.Code, contentDescription = null, tint = AccentCyan) },
                            modifier = Modifier.fillMaxWidth()
                        )

                        Spacer(modifier = Modifier.height(24.dp))

                        Button(
                            onClick = { viewModel.saveBeneficiary() },
                            modifier = Modifier.fillMaxWidth(),
                            colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue)
                        ) {
                            Icon(Icons.Default.Save, contentDescription = null, modifier = Modifier.size(18.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("SAVE & REGISTER WITH FUSION", fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }

    if (isSaved) {
        AlertDialog(
            onDismissRequest = { viewModel.resetSaved(); onBack() },
            containerColor = SurfaceDark,
            title = {
                Text("Beneficiary Added", color = StatusGreen, fontWeight = FontWeight.Bold)
            },
            text = {
                Text("Beneficiary saved successfully. Telemetry event BENEFICIARY_ADDED streamed to Fusion Risk OS.", color = TextPrimaryDark)
            },
            confirmButton = {
                Button(onClick = { viewModel.resetSaved(); onBack() }) {
                    Text("OK")
                }
            }
        )
    }
}
