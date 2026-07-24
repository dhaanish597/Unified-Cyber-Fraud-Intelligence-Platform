package com.fusionbank.mobileapp

import android.app.Application
import com.fusionbank.mobileapp.sdk.Fusion
import com.fusionbank.mobileapp.sdk.FusionConfig
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class FusionBankApp : Application() {
    override fun onCreate() {
        super.onCreate()
        // Initialize Fusion Adaptive Trust SDK
        Fusion.initialize(
            context = this,
            customConfig = FusionConfig(
                baseUrl = BuildConfig.FUSION_BASE_URL,
                wsUrl = BuildConfig.FUSION_WS_URL,
                appId = "com.fusionbank.mobileapp",
                tenantId = BuildConfig.TENANT_ID,
                sdkVersion = BuildConfig.SDK_VERSION,
                environment = if (BuildConfig.DEBUG) "DEVELOPMENT" else "PRODUCTION",
                developmentClientId = BuildConfig.FUSION_DEV_CLIENT_ID.ifBlank { null },
                developmentClientSecret = BuildConfig.FUSION_DEV_CLIENT_SECRET.ifBlank { null }
            )
        )
    }
}
