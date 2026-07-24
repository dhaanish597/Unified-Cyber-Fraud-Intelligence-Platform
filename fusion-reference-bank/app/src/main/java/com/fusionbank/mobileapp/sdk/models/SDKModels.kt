package com.fusionbank.mobileapp.sdk.models

import com.google.gson.annotations.SerializedName

data class SDKTokenRequest(
    @SerializedName("client_id") val clientId: String,
    @SerializedName("client_secret") val clientSecret: String
)

data class PairingRegistrationRequest(
    @SerializedName("pair_id") val pairId: String,
    @SerializedName("bootstrap_token") val bootstrapToken: String,
    @SerializedName("device_uuid") val deviceUuid: String,
    @SerializedName("android_version") val androidVersion: String,
    val manufacturer: String,
    val model: String,
    @SerializedName("sdk_version") val sdkVersion: String,
    @SerializedName("app_version") val appVersion: String,
    val fingerprint: String,
)

data class PairingRegistrationResponse(
    @SerializedName("device_id") val deviceId: String,
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("refresh_token") val refreshToken: String,
    @SerializedName("session_token") val sessionToken: String,
    @SerializedName("expires_at") val expiresAt: Long,
    @SerializedName("backend_url") val backendUrl: String,
    @SerializedName("ws_url") val wsUrl: String,
)

data class SDKTokenResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("expires_at") val expiresAt: Long,
    @SerializedName("refresh_token") val refreshToken: String? = null,
    @SerializedName("refresh_expires_at") val refreshExpiresAt: Long? = null
)

data class BankingLoginRequest(
    @SerializedName("username") val username: String,
    @SerializedName("password") val password: String,
    @SerializedName("device_id") val deviceId: String
)

data class BankingRefreshRequest(
    @SerializedName("refresh_token") val refreshToken: String,
    @SerializedName("device_id") val deviceId: String
)

data class BankingLogoutRequest(
    @SerializedName("refresh_token") val refreshToken: String?
)

data class BankingProfile(
    @SerializedName("user_id") val userId: String,
    @SerializedName("username") val username: String,
    @SerializedName("display_name") val displayName: String,
    @SerializedName("email") val email: String,
    @SerializedName("tenant_id") val tenantId: String
)

data class BankingAuthResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("expires_at") val expiresAt: Long,
    @SerializedName("refresh_token") val refreshToken: String,
    @SerializedName("refresh_expires_at") val refreshExpiresAt: Long,
    @SerializedName("profile") val profile: BankingProfile
)

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
    @SerializedName("composite_trust_score") val compositeTrustScore: Float?,
    @SerializedName("device_trust") val deviceTrust: Float?,
    @SerializedName("session_trust") val sessionTrust: Float?,
    @SerializedName("behaviour_trust") val behaviourTrust: Float?,
    @SerializedName("network_trust") val networkTrust: Float?,
    @SerializedName("runtime_trust") val runtimeTrust: Float?,
    @SerializedName("trust_status") val trustStatus: String = "PENDING_AUTHORITATIVE_EVIDENCE"
    ,
    @SerializedName("request_id") val requestId: String? = null,
    @SerializedName("correlation_id") val correlationId: String? = null,
    @SerializedName("pipeline_id") val pipelineId: String? = null,
    @SerializedName("backend_ack") val backendAck: Boolean = false
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
    @SerializedName("device_trust_score") val deviceTrustScore: Float?,
    @SerializedName("runtime_trust_score") val runtimeTrustScore: Float?
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
    @SerializedName("network_trust_score") val networkTrustScore: Float?
)

data class SDKEventRequest(
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("device_id") val deviceId: String,
    @SerializedName("event_type") val eventType: String,
    @SerializedName("amount") val amount: Double = 0.0,
    @SerializedName("sdk_version") val sdkVersion: String = "FAT-SDK v2.4.1",
    @SerializedName("request_id") val requestId: String,
    @SerializedName("correlation_id") val correlationId: String
)

data class SDKEventResponse(
    @SerializedName("event_id") val eventId: String,
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("event_type") val eventType: String,
    @SerializedName("timestamp") val timestamp: String,
    @SerializedName("ingestion_latency_ms") val ingestionLatencyMs: Float,
    @SerializedName("request_id") val requestId: String?,
    @SerializedName("correlation_id") val correlationId: String?,
    @SerializedName("pipeline_id") val pipelineId: String?,
    @SerializedName("backend_ack") val backendAck: Boolean
)

data class SDKDecisionRequest(
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("event_type") val eventType: String,
    @SerializedName("amount") val amount: Double,
    @SerializedName("vpn_detected") val vpnDetected: Boolean = false,
    @SerializedName("root_detected") val rootDetected: Boolean = false,
    @SerializedName("beneficiary_id") val beneficiaryId: String? = null,
    @SerializedName("request_id") val requestId: String,
    @SerializedName("correlation_id") val correlationId: String
)

data class SDKDecisionResponse(
    @SerializedName("decision_id") val decisionId: String,
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("decision") val decision: String,
    @SerializedName("confidence") val confidence: Float?,
    @SerializedName("reason_codes") val reasonCodes: List<String>,
    @SerializedName("recommended_action") val recommendedAction: String,
    @SerializedName("policy_version") val policyVersion: String,
    @SerializedName("decision_latency_ms") val decisionLatencyMs: Float,
    @SerializedName("pipeline_id") val pipelineId: String,
    @SerializedName("request_id") val requestId: String,
    @SerializedName("correlation_id") val correlationId: String,
    @SerializedName("backend_ack") val backendAck: Boolean,
    @SerializedName("model_status") val modelStatus: String,
    @SerializedName("model_error_code") val modelErrorCode: String?,
    @SerializedName("graph_status") val graphStatus: String,
    @SerializedName("graph_backend") val graphBackend: String
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
    @SerializedName("passport_id") val passportId: String = "",
    @SerializedName("user_id") val userId: String = "",
    @SerializedName("identity_trust") val identityTrust: Float = 0f,
    @SerializedName("device_trust") val deviceTrust: Float = 0f,
    @SerializedName("runtime_trust") val runtimeTrust: Float = 0f,
    @SerializedName("behaviour_trust") val behaviourTrust: Float = 0f,
    @SerializedName("network_trust") val networkTrust: Float = 0f,
    @SerializedName("geo_trust") val geoTrust: Float = 0f,
    @SerializedName("threat_trust") val threatTrust: Float = 0f,
    @SerializedName("graph_trust") val graphTrust: Float = 0f,
    @SerializedName("transaction_trust") val transactionTrust: Float = 0f,
    @SerializedName("overall_trust") val overallTrust: Float = 0f,
    @SerializedName("confidence") val confidence: Float = 0f,
    @SerializedName("current_status") val currentStatus: String = "ACTIVE",
    @SerializedName("created_time") val createdTime: String = "",
    @SerializedName("updated_time") val updatedTime: String = "",
    @SerializedName("version") val version: String = "",
    @SerializedName("trust_trend") val trustTrend: String = "STABLE",
    @SerializedName("components") val components: Map<String, SDKTrustComponent> = emptyMap(),
    @SerializedName("composite_trust") val compositeTrust: Float = overallTrust,
    @SerializedName("session_trust") val sessionTrust: Float = overallTrust,
    @SerializedName("policy_version") val policyVersion: String = version,
    @SerializedName("sync_timestamp") val syncTimestamp: String = updatedTime
)

data class SDKTrustComponent(
    @SerializedName("name") val name: String,
    @SerializedName("value") val value: Float,
    @SerializedName("confidence") val confidence: Float?,
    @SerializedName("previous_value") val previousValue: Float,
    @SerializedName("difference") val difference: Float,
    @SerializedName("trend") val trend: String,
    @SerializedName("reasons") val reasons: List<String> = emptyList(),
    @SerializedName("updated_at") val updatedAt: String = ""
)

data class SDKTrustDelta(
    @SerializedName("delta_id") val deltaId: String,
    @SerializedName("timestamp") val timestamp: String,
    @SerializedName("event_type") val eventType: String,
    @SerializedName("component") val component: String,
    @SerializedName("previous_trust") val previousTrust: Float,
    @SerializedName("current_trust") val currentTrust: Float,
    @SerializedName("difference") val difference: Float,
    @SerializedName("reason") val reason: String,
    @SerializedName("is_recovery") val isRecovery: Boolean = false
)

data class SDKTrustSnapshot(
    @SerializedName("snapshot_id") val snapshotId: String,
    @SerializedName("timestamp") val timestamp: String,
    @SerializedName("event_type") val eventType: String,
    @SerializedName("previous_trust") val previousTrust: Float,
    @SerializedName("current_trust") val currentTrust: Float,
    @SerializedName("delta") val delta: Float,
    @SerializedName("reason") val reason: String
)

data class SDKTrustHistoryResponse(
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("range") val range: String,
    @SerializedName("snapshots") val snapshots: List<SDKTrustSnapshot>,
    @SerializedName("count") val count: Int
)

data class SDKTrustUpdateEnvelope(
    @SerializedName("msg_type") val messageType: String,
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("event_type") val eventType: String,
    @SerializedName("passport") val passport: SDKTrustPassportResponse,
    @SerializedName("deltas") val deltas: List<SDKTrustDelta> = emptyList(),
    @SerializedName("snapshot") val snapshot: SDKTrustSnapshot? = null,
    @SerializedName("processing_time_ms") val processingTimeMs: Float = 0f
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
