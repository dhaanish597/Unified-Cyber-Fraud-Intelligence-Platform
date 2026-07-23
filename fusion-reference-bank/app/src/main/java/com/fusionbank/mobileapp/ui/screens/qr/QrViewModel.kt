package com.fusionbank.mobileapp.ui.screens.qr

import androidx.lifecycle.ViewModel
import com.fusionbank.mobileapp.sdk.Fusion
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject

@HiltViewModel
class QrViewModel @Inject constructor() : ViewModel() {
    private val _merchant = MutableStateFlow("Starbucks Cyber City")
    val merchant: StateFlow<String> = _merchant.asStateFlow()

    private val _amount = MutableStateFlow("450.00")
    val amount: StateFlow<String> = _amount.asStateFlow()

    private val _isCompleted = MutableStateFlow(false)
    val isCompleted: StateFlow<Boolean> = _isCompleted.asStateFlow()

    fun onMerchantChanged(v: String) { _merchant.value = v }
    fun onAmountChanged(v: String) { _amount.value = v }

    fun processQrPayment() {
        val amt = _amount.value.toDoubleOrNull() ?: 0.0
        Fusion.reportEvent("QR_PAYMENT", amt)
        _isCompleted.value = true
    }

    fun reset() { _isCompleted.value = false }
}
