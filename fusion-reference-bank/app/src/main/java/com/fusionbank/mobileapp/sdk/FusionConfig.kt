package com.fusionbank.mobileapp.sdk

data class FusionConfig(
    val baseUrl: String = "http://10.0.2.2:8001/",
    val wsUrl: String = "ws://10.0.2.2:8001/ws/stream",
    val appId: String = "com.fusionbank.mobileapp",
    val tenantId: String = "TENANT_FUSB_001",
    val sdkVersion: String = "FAT-SDK v2.4.1",
    val environment: String = "PRODUCTION"
)
