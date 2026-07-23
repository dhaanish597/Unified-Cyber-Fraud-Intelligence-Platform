package com.fusionbank.mobileapp.ui.screens.login

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.fusionbank.mobileapp.sdk.Fusion
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class LoginViewModel @Inject constructor() : ViewModel() {

    private val _username = MutableStateFlow("demo_user")
    val username: StateFlow<String> = _username.asStateFlow()

    private val _password = MutableStateFlow("••••••••")
    val password: StateFlow<String> = _password.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()

    fun onUsernameChanged(newVal: String) { _username.value = newVal }
    fun onPasswordChanged(newVal: String) { _password.value = newVal }

    fun login(onSuccess: () -> Unit) {
        if (_username.value.isBlank()) {
            _errorMessage.value = "Please enter username"
            return
        }

        _isLoading.value = true
        _errorMessage.value = null

        Fusion.startSession(_username.value) { result ->
            _isLoading.value = false
            result.onSuccess {
                onSuccess()
            }.onFailure { ex ->
                _errorMessage.value = ex.message ?: "Authentication / SDK Session failed"
            }
        }
    }
}
