package com.fusionbank.mobileapp.sdk.models

import com.google.gson.annotations.SerializedName

data class SDKSessionStartRequest(
    @SerializedName("app_id") val appId: String = "com.fusionbank.mobileapp",
    @SerializedName("tenant_id") val tenantId: String = "TENANT_FUSB_001",
    @SerializedName("sdk_version") val sdkVersion: String = "FAT-SDK v2.4.1",
    @SerializedName("user_id") val userId: String,
    @SerializedName("device_id") val deviceId: String,
    @SerializedName("environment") val environment: String = "PRODUCTION"
)

data class SDKSessionResponse(
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("app_id") val appId: String,
    @SerializedName("tenant_id") val tenantId: String,
    @SerializedName("sdk_version") val sdkVersion: String,
    @SerializedName("user_id") val userId: String,
    @SerializedName("device_id") val deviceId: String,
    @SerializedName("environment") val environment: String,
    @SerializedName("started_at") val startedAt: String,
    @SerializedName("status") val status: String,
    @SerializedName("policy_version") val policyVersion: String,
    @SerializedName("composite_trust_score") val compositeTrustScore: Float,
    @SerializedName("device_trust") val deviceTrust: Float,
    @SerializedName("session_trust") val sessionTrust: Float,
    @SerializedName("behaviour_trust") val behaviourTrust: Float,
    @SerializedName("network_trust") val networkTrust: Float,
    @SerializedName("runtime_trust") val runtimeTrust: Float
)

data class SDKDeviceRequest(
    @SerializedName("device_id") val deviceId: String,
    @SerializedName("model") val model: String,
    @SerializedName("manufacturer") val manufacturer: String,
    @SerializedName("android_version") val androidVersion: String,
    @SerializedName("security_patch") val securityPatch: String,
    @SerializedName("screen_lock_enabled") val screenLockEnabled: Boolean,
    @SerializedName("root_detected") val rootDetected: Boolean,
    @SerializedName("emulator_detected") val emulatorDetected: Boolean,
    @SerializedName("frida_detected") val fridaDetected: Boolean,
    @SerializedName("debugger_attached") val debuggerAttached: Boolean,
    @SerializedName("overlay_detected") val overlayDetected: Boolean,
    @SerializedName("timezone") val timezone: String,
    @SerializedName("locale") val locale: String
)

data class SDKDeviceResponse(
    @SerializedName("device_id") val deviceId: String,
    @SerializedName("fingerprint") val fingerprint: String,
    @SerializedName("play_integrity_status") val playIntegrityStatus: String,
    @SerializedName("device_trust_score") val deviceTrustScore: Float,
    @SerializedName("runtime_trust_score") val runtimeTrustScore: Float
)

data class SDKNetworkRequest(
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("network_type") val networkType: String,
    @SerializedName("carrier") val carrier: String,
    @SerializedName("vpn_detected") val vpnDetected: Boolean,
    @SerializedName("proxy_detected") val proxyDetected: Boolean,
    @SerializedName("roaming") val roaming: Boolean,
    @SerializedName("wifi_vs_cellular") val wifiVsCellular: String
)

data class SDKNetworkResponse(
    @SerializedName("network_type") val networkType: String,
    @SerializedName("carrier") val carrier: String,
    @SerializedName("vpn_detected") val vpnDetected: Boolean,
    @SerializedName("proxy_detected") val proxyDetected: Boolean,
    @SerializedName("network_trust_score") val networkTrustScore: Float
)

data class SDKEventRequest(
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("device_id") val deviceId: String,
    @SerializedName("event_type") val eventType: String,
    @SerializedName("amount") val amount: Double = 0.0,
    @SerializedName("composite_trust") val compositeTrust: Float = 82.0f,
    @SerializedName("sdk_version") val sdkVersion: String = "FAT-SDK v2.4.1"
)

data class SDKEventResponse(
    @SerializedName("event_id") val eventId: String,
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("event_type") val eventType: String,
    @SerializedName("timestamp") val timestamp: String,
    @SerializedName("ingestion_latency_ms") val ingestionLatencyMs: Float
)

data class SDKDecisionRequest(
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("event_type") val eventType: String,
    @SerializedName("amount") val amount: Double,
    @SerializedName("composite_trust") val compositeTrust: Float,
    @SerializedName("vpn_detected") val vpnDetected: Boolean = false,
    @SerializedName("root_detected") val rootDetected: Boolean = false,
    @SerializedName("runtime_trust") val runtimeTrust: Float = 94.0f
)

data class SDKDecisionResponse(
    @SerializedName("decision_id") val decisionId: String,
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("decision") val decision: String,
    @SerializedName("confidence") val confidence: Float,
    @SerializedName("reason_codes") val reasonCodes: List<String>,
    @SerializedName("recommended_action") val recommendedAction: String,
    @SerializedName("policy_version") val policyVersion: String,
    @SerializedName("decision_latency_ms") val decisionLatencyMs: Float
)

data class SDKPoliciesResponse(
    @SerializedName("policies") val policies: List<SDKPolicy>,
    @SerializedName("policy_version") val policyVersion: String
)

data class SDKPolicy(
    @SerializedName("id") val id: String,
    @SerializedName("name") val name: String,
    @SerializedName("trigger") val trigger: String,
    @SerializedName("action") val action: String,
    @SerializedName("priority") val priority: String,
    @SerializedName("active") val active: Boolean,
    @SerializedName("version") val version: String
)

data class SDKTrustPassportResponse(
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("composite_trust") val compositeTrust: Float,
    @SerializedName("device_trust") val deviceTrust: Float,
    @SerializedName("session_trust") val sessionTrust: Float,
    @SerializedName("behaviour_trust") val behaviourTrust: Float,
    @SerializedName("network_trust") val networkTrust: Float,
    @SerializedName("runtime_trust") val runtimeTrust: Float,
    @SerializedName("policy_version") val policyVersion: String,
    @SerializedName("sync_timestamp") val syncTimestamp: String
)

data class SDKHealthResponse(
    @SerializedName("sdk_health") val sdkHealth: String,
    @SerializedName("connection_status") val connectionStatus: String,
    @SerializedName("active_sessions") val activeSessions: Int,
    @SerializedName("total_events_processed") val totalEventsProcessed: Int,
    @SerializedName("average_latency_ms") val averageLatencyMs: Float,
    @SerializedName("policy_version") val policyVersion: String
)

enum class FusionConnectionState {
    CONNECTED,
    SYNCING,
    DISCONNECTED
}
