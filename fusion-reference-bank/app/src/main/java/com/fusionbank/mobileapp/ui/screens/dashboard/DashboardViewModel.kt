package com.fusionbank.mobileapp.ui.screens.dashboard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.fusionbank.mobileapp.sdk.Fusion
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class BankAccount(
    val accountNumber: String,
    val accountType: String,
    val balance: Double,
    val currency: String = "INR"
)

data class TransactionItem(
    val id: String,
    val title: String,
    val date: String,
    val amount: Double,
    val type: String
)

@HiltViewModel
class DashboardViewModel @Inject constructor() : ViewModel() {

    private val _accounts = MutableStateFlow(
        listOf(
            BankAccount("102938475612", "Savings Account", 248950.00),
            BankAccount("987654321098", "Current Account", 1250000.50)
        )
    )
    val accounts: StateFlow<List<BankAccount>> = _accounts.asStateFlow()

    private val _recentTransactions = MutableStateFlow(
        listOf(
            TransactionItem("TXN_8801", "Amazon Online Payment", "23 Jul 2026", -2499.00, "BILL_PAYMENT"),
            TransactionItem("TXN_8802", "Salary Credit - Acme Corp", "20 Jul 2026", 185000.00, "CREDIT"),
            TransactionItem("TXN_8803", "QR Scan - Star Cafe", "19 Jul 2026", -350.00, "QR_PAYMENT")
        )
    )
    val recentTransactions: StateFlow<List<TransactionItem>> = _recentTransactions.asStateFlow()

    init {
        // Stream telemetry event for HOME_VISITED
        Fusion.reportEvent("HOME_VISITED")
        Fusion.getTrustPassport { }
    }
}
