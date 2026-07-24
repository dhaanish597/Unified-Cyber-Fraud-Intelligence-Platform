package com.fusionbank.mobileapp.sdk

data class FusionConfig(
    val baseUrl: String = "https://fusion.example.invalid/",
    val wsUrl: String = "wss://fusion.example.invalid/ws/stream",
    val appId: String = "com.fusionbank.mobileapp",
    val tenantId: String = "TENANT_FUSB_001",
    val sdkVersion: String = "FAT-SDK v2.4.1",
    val environment: String = "PRODUCTION",
    val accessToken: String? = null,
    val developmentClientId: String? = null,
    val developmentClientSecret: String? = null
)
