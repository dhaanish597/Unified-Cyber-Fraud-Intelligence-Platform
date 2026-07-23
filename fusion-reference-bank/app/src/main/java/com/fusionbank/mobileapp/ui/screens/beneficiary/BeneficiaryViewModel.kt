package com.fusionbank.mobileapp.ui.screens.beneficiary

import androidx.lifecycle.ViewModel
import com.fusionbank.mobileapp.sdk.Fusion
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject

@HiltViewModel
class BeneficiaryViewModel @Inject constructor() : ViewModel() {

    private val _name = MutableStateFlow("")
    val name: StateFlow<String> = _name.asStateFlow()

    private val _account = MutableStateFlow("")
    val account: StateFlow<String> = _account.asStateFlow()

    private val _ifsc = MutableStateFlow("")
    val ifsc: StateFlow<String> = _ifsc.asStateFlow()

    private val _isSaved = MutableStateFlow(false)
    val isSaved: StateFlow<Boolean> = _isSaved.asStateFlow()

    fun onNameChanged(v: String) { _name.value = v }
    fun onAccountChanged(v: String) { _account.value = v }
    fun onIfscChanged(v: String) { _ifsc.value = v }

    fun saveBeneficiary() {
        if (_name.value.isBlank() || _account.value.isBlank()) return

        // Stream telemetry event for BENEFICIARY_ADDED
        Fusion.reportEvent("BENEFICIARY_ADDED")
        _isSaved.value = true
    }

    fun resetSaved() { _isSaved.value = false }
}
