package com.fusionbank.mobileapp.ui.screens.simulator

data class ThreatScenario(
    val id: String,
    val title: String,
    val description: String,
    val threatLevel: String, // CRITICAL, HIGH, MEDIUM, LOW
    val eventsToSimulate: List<ScenarioEvent>
)

data class ScenarioEvent(
    val eventType: String,
    val amount: Double = 0.0,
    val delayMs: Long = 300L,
    val isDeviceThreat: Boolean = false,
    val isNetworkThreat: Boolean = false,
    val isDecisionRequest: Boolean = false
)

object DemoScenarioLibrary {

    val scenarios = listOf(
        ThreatScenario(
            id = "SCEN_NORMAL",
            title = "Normal Customer",
            description = "Clean device profile, trusted network, standard user behavior.",
            threatLevel = "LOW",
            eventsToSimulate = listOf(
                ScenarioEvent(eventType = "USER_LOGIN"),
                ScenarioEvent(eventType = "HOME_VISITED", delayMs = 200),
                ScenarioEvent(eventType = "TRANSFER_INITIATED", amount = 1200.0, isDecisionRequest = true)
            )
        ),
        ThreatScenario(
            id = "SCEN_ATO",
            title = "Account Takeover (ATO)",
            description = "Impossible travel detected, new device fingerprint, active VPN, password reset attempt followed by large transfer.",
            threatLevel = "CRITICAL",
            eventsToSimulate = listOf(
                ScenarioEvent(eventType = "IMPOSSIBLE_TRAVEL"),
                ScenarioEvent(eventType = "NEW_DEVICE_DETECTED"),
                ScenarioEvent(eventType = "VPN_ENABLED", isNetworkThreat = true),
                ScenarioEvent(eventType = "PASSWORD_RESET_ATTEMPT"),
                ScenarioEvent(eventType = "TRANSFER_INITIATED", amount = 250000.0, isDecisionRequest = true)
            )
        ),
        ThreatScenario(
            id = "SCEN_COMPROMISED",
            title = "Compromised Device",
            description = "Rooted device with Magisk, overlay attack detected, accessibility service abuse, and attached debugger.",
            threatLevel = "CRITICAL",
            eventsToSimulate = listOf(
                ScenarioEvent(eventType = "ROOT_DETECTED", isDeviceThreat = true),
                ScenarioEvent(eventType = "OVERLAY_DETECTED"),
                ScenarioEvent(eventType = "ACCESSIBILITY_ABUSE"),
                ScenarioEvent(eventType = "DEBUGGER_ATTACHED", isDeviceThreat = true),
                ScenarioEvent(eventType = "TRANSFER_INITIATED", amount = 75000.0, isDecisionRequest = true)
            )
        ),
        ThreatScenario(
            id = "SCEN_INSIDER",
            title = "Insider Threat",
            description = "High velocity access, bulk data export behavior, concurrent session anomaly.",
            threatLevel = "HIGH",
            eventsToSimulate = listOf(
                ScenarioEvent(eventType = "CONCURRENT_SESSION_DETECTED"),
                ScenarioEvent(eventType = "HIGH_VELOCITY_NAVIGATION"),
                ScenarioEvent(eventType = "BULK_DATA_EXPORT_ATTEMPT"),
                ScenarioEvent(eventType = "TRANSFER_INITIATED", amount = 180000.0, isDecisionRequest = true)
            )
        ),
        ThreatScenario(
            id = "SCEN_MULE",
            title = "Money Mule Campaign",
            description = "Rapid beneficiary addition, beneficiary linked to mule cluster, high velocity rapid transfers.",
            threatLevel = "CRITICAL",
            eventsToSimulate = listOf(
                ScenarioEvent(eventType = "BENEFICIARY_ADDED"),
                ScenarioEvent(eventType = "MULE_CLUSTER_CORRELATION"),
                ScenarioEvent(eventType = "RAPID_TRANSFER_SEQUENCE", amount = 95000.0),
                ScenarioEvent(eventType = "TRANSFER_INITIATED", amount = 95000.0, isDecisionRequest = true)
            )
        ),
        ThreatScenario(
            id = "SCEN_SOCIAL_ENG",
            title = "Social Engineering / Remote Control",
            description = "Active accessibility overlay hijacking screen, rapid forced navigation, victim guided through large transfer.",
            threatLevel = "HIGH",
            eventsToSimulate = listOf(
                ScenarioEvent(eventType = "ACCESSIBILITY_OVERLAY_ACTIVE"),
                ScenarioEvent(eventType = "REMOTE_ACCESS_TOOL_DETECTED"),
                ScenarioEvent(eventType = "FAST_GUIDED_NAVIGATION"),
                ScenarioEvent(eventType = "TRANSFER_INITIATED", amount = 150000.0, isDecisionRequest = true)
            )
        ),
        ThreatScenario(
            id = "SCEN_MALWARE",
            title = "Malware & Frida Injection",
            description = "Frida instrumentation framework detected, runtime hooking, memory modification, certificate pinning bypass.",
            threatLevel = "CRITICAL",
            eventsToSimulate = listOf(
                ScenarioEvent(eventType = "FRIDA_INSTRUMENTATION_DETECTED", isDeviceThreat = true),
                ScenarioEvent(eventType = "RUNTIME_HOOK_DETECTED"),
                ScenarioEvent(eventType = "MEMORY_TAMPERING"),
                ScenarioEvent(eventType = "CERTIFICATE_PINNING_FAILURE"),
                ScenarioEvent(eventType = "TRANSFER_INITIATED", amount = 500000.0, isDecisionRequest = true)
            )
        ),
        ThreatScenario(
            id = "SCEN_QR_FRAUD",
            title = "QR Payment Fraud",
            description = "Scan malicious spoofed QR code, new unverified merchant, high value QR payment.",
            threatLevel = "MEDIUM",
            eventsToSimulate = listOf(
                ScenarioEvent(eventType = "SPOOFED_QR_SCAN"),
                ScenarioEvent(eventType = "UNVERIFIED_MERCHANT"),
                ScenarioEvent(eventType = "QR_PAYMENT", amount = 45000.0, isDecisionRequest = true)
            )
        ),
        ThreatScenario(
            id = "SCEN_SIM_SWAP",
            title = "SIM Swap Attack",
            description = "SIM card change detected, OTP interception attempt, rapid credential re-authentication.",
            threatLevel = "HIGH",
            eventsToSimulate = listOf(
                ScenarioEvent(eventType = "SIM_CARD_CHANGED"),
                ScenarioEvent(eventType = "OTP_INTERCEPTION_ATTEMPT"),
                ScenarioEvent(eventType = "REPEATED_OTP_FAILURE"),
                ScenarioEvent(eventType = "TRANSFER_INITIATED", amount = 85000.0, isDecisionRequest = true)
            )
        ),
        ThreatScenario(
            id = "SCEN_CRED_STUFF",
            title = "Credential Stuffing",
            description = "Rapid automated login attempts, distributed proxy network, failed auth surge.",
            threatLevel = "HIGH",
            eventsToSimulate = listOf(
                ScenarioEvent(eventType = "PROXY_DETECTED", isNetworkThreat = true),
                ScenarioEvent(eventType = "CREDENTIAL_STUFFING_SURGE"),
                ScenarioEvent(eventType = "FAILED_AUTH_SERIES"),
                ScenarioEvent(eventType = "USER_LOGIN", isDecisionRequest = true)
            )
        )
    )
}
