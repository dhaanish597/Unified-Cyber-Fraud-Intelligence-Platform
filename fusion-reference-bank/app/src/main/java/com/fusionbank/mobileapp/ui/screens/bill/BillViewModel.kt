package com.fusionbank.mobileapp.ui.screens.bill

import androidx.lifecycle.ViewModel
import com.fusionbank.mobileapp.sdk.Fusion
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject

@HiltViewModel
class BillViewModel @Inject constructor() : ViewModel() {
    private val _category = MutableStateFlow("Electricity")
    val category: StateFlow<String> = _category.asStateFlow()

    private val _amount = MutableStateFlow("2450.00")
    val amount: StateFlow<String> = _amount.asStateFlow()

    private val _isCompleted = MutableStateFlow(false)
    val isCompleted: StateFlow<Boolean> = _isCompleted.asStateFlow()

    fun onCategoryChanged(v: String) { _category.value = v }
    fun onAmountChanged(v: String) { _amount.value = v }

    fun processBillPayment() {
        val amt = _amount.value.toDoubleOrNull() ?: 0.0
        Fusion.reportEvent("BILL_PAYMENT", amt)
        _isCompleted.value = true
    }

    fun reset() { _isCompleted.value = false }
}
