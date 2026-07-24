package com.fusionbank.mobileapp.ui.screens.profile

import androidx.lifecycle.ViewModel
import com.fusionbank.mobileapp.BuildConfig
import com.fusionbank.mobileapp.sdk.Fusion
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject

@HiltViewModel
class ProfileViewModel @Inject constructor() : ViewModel() {

    val endpoint: String = BuildConfig.FUSION_BASE_URL
    val sdkVersion: String = BuildConfig.SDK_VERSION

    fun logout(onLoggedOut: () -> Unit) {
        Fusion.logout {
            onLoggedOut()
        }
    }
}
