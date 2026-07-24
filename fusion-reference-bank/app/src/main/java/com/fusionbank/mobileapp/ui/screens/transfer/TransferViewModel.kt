package com.fusionbank.mobileapp.ui.screens.transfer

import androidx.lifecycle.ViewModel
import com.fusionbank.mobileapp.sdk.Fusion
import com.fusionbank.mobileapp.sdk.models.SDKDecisionResponse
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject

@HiltViewModel
class TransferViewModel @Inject constructor() : ViewModel() {

    private val _recipient = MutableStateFlow("usr_mule_cluster_alpha")
    val recipient: StateFlow<String> = _recipient.asStateFlow()

    private val _amount = MutableStateFlow("75000")
    val amount: StateFlow<String> = _amount.asStateFlow()

    private val _remarks = MutableStateFlow("Urgent Transfer")
    val remarks: StateFlow<String> = _remarks.asStateFlow()

    private val _isEvaluating = MutableStateFlow(false)
    val isEvaluating: StateFlow<Boolean> = _isEvaluating.asStateFlow()

    private val _decisionResult = MutableStateFlow<SDKDecisionResponse?>(null)
    val decisionResult: StateFlow<SDKDecisionResponse?> = _decisionResult.asStateFlow()

    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()

    fun onRecipientChanged(v: String) { _recipient.value = v }
    fun onAmountChanged(v: String) { _amount.value = v }
    fun onRemarksChanged(v: String) { _remarks.value = v }

    fun submitTransfer() {
        val amt = _amount.value.toDoubleOrNull()
        if (amt == null || amt <= 0) {
            _errorMessage.value = "Enter valid transfer amount"
            return
        }

        _isEvaluating.value = true
        _errorMessage.value = null
        _decisionResult.value = null

        Fusion.requestDecision(
            eventType = "TRANSFER_INITIATED",
            amount = amt,
            beneficiaryId = _recipient.value
        ) { result ->
            _isEvaluating.value = false
            result.onSuccess { decision ->
                _decisionResult.value = decision
            }.onFailure { ex ->
                _errorMessage.value = ex.message ?: "Decision request failed"
            }
        }
    }

    fun dismissResult() {
        _decisionResult.value = null
    }
}
