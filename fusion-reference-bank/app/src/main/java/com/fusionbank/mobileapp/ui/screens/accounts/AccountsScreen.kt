package com.fusionbank.mobileapp.ui.screens.accounts

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CreditCard
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.fusionbank.mobileapp.sdk.Fusion
import com.fusionbank.mobileapp.ui.components.LiveStatusCard
import com.fusionbank.mobileapp.ui.theme.*

data class AccountDetail(
    val title: String,
    val accountNumber: String,
    val ifsc: String,
    val balance: Double,
    val type: String
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AccountsScreen(
    onBack: () -> Unit
) {
    LaunchedEffect(Unit) {
        Fusion.reportEvent("ACCOUNTS_VISITED")
    }

    val accountList = listOf(
        AccountDetail("Primary Savings Account", "102938475612", "MAHB0001029", 248950.00, "SAVINGS"),
        AccountDetail("Corporate Current Account", "987654321098", "MAHB0001029", 1250000.50, "CURRENT"),
        AccountDetail("Fixed Deposit - 12 Months", "554433221100", "MAHB0001029", 500000.00, "FD")
    )

    Scaffold(
        containerColor = PrimaryDark,
        topBar = {
            TopAppBar(
                title = { Text("My Accounts & Balances", color = TextPrimaryDark) },
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
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                items(accountList) { acc ->
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                        shape = RoundedCornerShape(16.dp)
                    ) {
                        Column(modifier = Modifier.padding(20.dp)) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(acc.title, style = MaterialTheme.typography.titleMedium, color = TextPrimaryDark)
                                Icon(Icons.Default.CreditCard, contentDescription = null, tint = AccentCyan)
                            }
                            Spacer(modifier = Modifier.height(12.dp))
                            Text(
                                "₹ ${String.format("%,.2f", acc.balance)}",
                                style = MaterialTheme.typography.titleLarge.copy(fontSize = 26.sp),
                                color = StatusGreen,
                                fontWeight = FontWeight.Bold
                            )
                            Spacer(modifier = Modifier.height(12.dp))
                            Divider(color = CardBorderDark, thickness = 0.5.dp)
                            Spacer(modifier = Modifier.height(8.dp))
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text("A/C No: ${acc.accountNumber}", style = MaterialTheme.typography.labelSmall, color = TextSecondaryDark)
                                Text("IFSC: ${acc.ifsc}", style = MaterialTheme.typography.labelSmall, color = TextSecondaryDark)
                            }
                        }
                    }
                }
            }
        }
    }
}
