package com.fusionbank.mobileapp.ui.screens.dashboard

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.fusionbank.mobileapp.ui.components.LiveStatusCard
import com.fusionbank.mobileapp.ui.theme.*

@Composable
fun DashboardScreen(
    onNavigate: (String) -> Unit,
    viewModel: DashboardViewModel = hiltViewModel()
) {
    val accounts by viewModel.accounts.collectAsState()
    val transactions by viewModel.recentTransactions.collectAsState()

    Scaffold(
        containerColor = PrimaryDark,
        bottomBar = {
            NavigationBar(containerColor = SurfaceDark) {
                NavigationBarItem(
                    selected = true,
                    onClick = { },
                    icon = { Icon(Icons.Default.Home, contentDescription = "Home") },
                    label = { Text("Home") }
                )
                NavigationBarItem(
                    selected = false,
                    onClick = { onNavigate("accounts") },
                    icon = { Icon(Icons.Default.AccountBalanceWallet, contentDescription = "Accounts") },
                    label = { Text("Accounts") }
                )
                NavigationBarItem(
                    selected = false,
                    onClick = { onNavigate("transfer") },
                    icon = { Icon(Icons.Default.Send, contentDescription = "Transfer") },
                    label = { Text("Transfer") }
                )
                NavigationBarItem(
                    selected = false,
                    onClick = { onNavigate("profile") },
                    icon = { Icon(Icons.Default.Person, contentDescription = "Profile") },
                    label = { Text("Profile") }
                )
            }
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Persistent Live Fusion Risk OS Status Card
            LiveStatusCard()

            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Welcome Banner
                item {
                    Column {
                        Text("Welcome Back,", style = MaterialTheme.typography.bodyMedium, color = TextSecondaryDark)
                        Text("Demo Customer", style = MaterialTheme.typography.titleLarge, color = TextPrimaryDark, fontWeight = FontWeight.Bold)
                    }
                }

                // Primary Account Balance Card
                item {
                    val primaryAcc = accounts.firstOrNull()
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = PrimaryBlue),
                        shape = RoundedCornerShape(16.dp)
                    ) {
                        Column(modifier = Modifier.padding(20.dp)) {
                            Text(primaryAcc?.accountType ?: "Savings Account", color = TextPrimaryDark.copy(alpha = 0.8f))
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                "₹ ${String.format("%,.2f", primaryAcc?.balance ?: 0.0)}",
                                style = MaterialTheme.typography.titleLarge.copy(fontSize = 28.sp),
                                color = TextPrimaryDark,
                                fontWeight = FontWeight.Bold
                            )
                            Spacer(modifier = Modifier.height(12.dp))
                            Text("A/C: ${primaryAcc?.accountNumber}", color = TextPrimaryDark.copy(alpha = 0.7f), style = MaterialTheme.typography.labelSmall)
                        }
                    }
                }

                // Quick Action Grid
                item {
                    Text("Quick Services", style = MaterialTheme.typography.titleMedium, color = TextPrimaryDark)
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        QuickActionButton("Transfer", Icons.Default.Send) { onNavigate("transfer") }
                        QuickActionButton("Payee", Icons.Default.GroupAdd) { onNavigate("beneficiary") }
                        QuickActionButton("QR Pay", Icons.Default.QrCodeScanner) { onNavigate("qr_payment") }
                        QuickActionButton("Bills", Icons.Default.Receipt) { onNavigate("bill_payment") }
                    }
                }

                // Recent Transactions Header
                item {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("Recent Activity", style = MaterialTheme.typography.titleMedium, color = TextPrimaryDark)
                        TextButton(onClick = { onNavigate("accounts") }) {
                            Text("View All", color = AccentCyan)
                        }
                    }
                }

                // Transaction Items
                items(transactions) { txn ->
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(14.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(
                                    imageVector = if (txn.amount < 0) Icons.Default.ArrowUpward else Icons.Default.ArrowDownward,
                                    contentDescription = null,
                                    tint = if (txn.amount < 0) StatusRed else StatusGreen,
                                    modifier = Modifier.size(24.dp)
                                )
                                Spacer(modifier = Modifier.width(12.dp))
                                Column {
                                    Text(txn.title, style = MaterialTheme.typography.bodyLarge, color = TextPrimaryDark, fontWeight = FontWeight.SemiBold)
                                    Text("${txn.date} • ${txn.type}", style = MaterialTheme.typography.labelSmall, color = TextSecondaryDark)
                                }
                            }
                            Text(
                                text = "${if (txn.amount > 0) "+" else ""}₹ ${String.format("%,.2f", txn.amount)}",
                                style = MaterialTheme.typography.bodyLarge,
                                color = if (txn.amount < 0) TextPrimaryDark else StatusGreen,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }

                item { Spacer(modifier = Modifier.height(16.dp)) }
            }
        }
    }
}

@Composable
fun QuickActionButton(
    label: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    onClick: () -> Unit
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        IconButton(
            onClick = onClick,
            modifier = Modifier
                .size(56.dp)
                .background(SurfaceDark, RoundedCornerShape(16.dp))
        ) {
            Icon(icon, contentDescription = label, tint = AccentCyan)
        }
        Spacer(modifier = Modifier.height(4.dp))
        Text(label, style = MaterialTheme.typography.labelSmall, color = TextPrimaryDark)
    }
}
