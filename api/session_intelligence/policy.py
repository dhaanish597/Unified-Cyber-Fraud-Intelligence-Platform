from __future__ import annotations

from dataclasses import dataclass

from .models import ComponentName


TRUST_POLICY_VERSION = "trust-v1.0.0"

COMPONENT_WEIGHTS: dict[ComponentName, float] = {
    ComponentName.IDENTITY: 0.14,
    ComponentName.DEVICE: 0.13,
    ComponentName.RUNTIME: 0.13,
    ComponentName.BEHAVIOUR: 0.10,
    ComponentName.NETWORK: 0.10,
    ComponentName.GEO: 0.08,
    ComponentName.THREAT: 0.14,
    ComponentName.GRAPH: 0.08,
    ComponentName.TRANSACTION: 0.10,
}

LIFECYCLE_THRESHOLDS = {
    "suspicious_below": 70.0,
    "blocked_below": 30.0,
}


@dataclass(frozen=True)
class ContextSignalRule:
    component: ComponentName
    key: str
    impact: float
    confidence: float
    reason: str


# Context rules cover session posture facts that are not threat detection.
# Security threats already classified by CyberThreatEngine are consumed through
# their trust_impact fields and are never re-detected here.
EVENT_CONTEXT_SIGNALS: dict[str, tuple[ContextSignalRule, ...]] = {
    "BENEFICIARY_ADDED": (
        ContextSignalRule(
            ComponentName.BEHAVIOUR,
            "recent_beneficiary_change",
            -6.0,
            0.8,
            "A beneficiary was added during the active session",
        ),
    ),
    "PUBLIC_WIFI": (
        ContextSignalRule(
            ComponentName.NETWORK,
            "public_wifi",
            -12.0,
            0.85,
            "Session is using an observed public Wi-Fi network",
        ),
    ),
    "GPS_SPOOFED": (
        ContextSignalRule(
            ComponentName.GEO,
            "gps_spoofing",
            -28.0,
            0.9,
            "Device telemetry reported GPS spoofing",
        ),
    ),
    "REPEATED_OTP_FAILURE": (
        ContextSignalRule(
            ComponentName.IDENTITY,
            "otp_failures",
            -18.0,
            0.9,
            "Repeated OTP verification failures were observed",
        ),
    ),
    "PASSWORD_RESET_ATTEMPT": (
        ContextSignalRule(
            ComponentName.IDENTITY,
            "password_reset",
            -8.0,
            0.75,
            "Password reset activity occurred in the active session",
        ),
    ),
    "SCREEN_RECORDING": (
        ContextSignalRule(
            ComponentName.RUNTIME,
            "screen_recording",
            -15.0,
            0.85,
            "Screen recording was reported while the banking session was active",
        ),
    ),
    "TAP_INJECTION": (
        ContextSignalRule(
            ComponentName.RUNTIME,
            "tap_injection",
            -24.0,
            0.9,
            "Input telemetry reported a tap-injection condition",
        ),
    ),
}


RECOVERY_EVENTS: dict[str, tuple[tuple[ComponentName, str, str], ...]] = {
    "VPN_DISABLED": (
        (ComponentName.NETWORK, "threat:Anonymizing Network / VPN Tunnel Active", "VPN tunnel removed"),
        (ComponentName.THREAT, "threat:Anonymizing Network / VPN Tunnel Active", "VPN threat evidence resolved"),
    ),
    "PROXY_DISABLED": (
        (ComponentName.NETWORK, "threat:Anonymizing Network / VPN Tunnel Active", "Proxy route removed"),
        (ComponentName.THREAT, "threat:Anonymizing Network / VPN Tunnel Active", "Proxy threat evidence resolved"),
    ),
    "TRUSTED_NETWORK_RESTORED": (
        (ComponentName.NETWORK, "public_wifi", "Trusted network restored"),
    ),
    "BIOMETRIC_VERIFIED": (
        (ComponentName.IDENTITY, "otp_failures", "Biometric identity verification succeeded"),
        (ComponentName.IDENTITY, "password_reset", "Biometric identity verification succeeded"),
    ),
    "KNOWN_DEVICE_VERIFIED": (
        (ComponentName.IDENTITY, "threat:Impossible Travel & Geofence Anomaly", "Known device verified"),
        (ComponentName.DEVICE, "threat:Android Hardware Emulator Execution", "Known physical device verified"),
        (ComponentName.THREAT, "threat:Impossible Travel & Geofence Anomaly", "Identity threat evidence resolved"),
        (ComponentName.THREAT, "threat:Android Hardware Emulator Execution", "Device threat evidence resolved"),
    ),
    "RUNTIME_INTEGRITY_RESTORED": (
        (ComponentName.RUNTIME, "threat:Frida Dynamic Instrumentation Framework Active", "Runtime integrity restored"),
        (ComponentName.RUNTIME, "threat:Active Debugger Attached to Banking Process", "Debugger detached"),
        (ComponentName.RUNTIME, "screen_recording", "Screen recording stopped"),
        (ComponentName.RUNTIME, "tap_injection", "Input integrity restored"),
        (ComponentName.THREAT, "threat:Frida Dynamic Instrumentation Framework Active", "Runtime threat evidence resolved"),
        (ComponentName.THREAT, "threat:Active Debugger Attached to Banking Process", "Debugger threat evidence resolved"),
    ),
    "THREAT_CLEARED": (
        (ComponentName.THREAT, "*", "Active threat set cleared by verified recovery event"),
    ),
}


THREAT_IMPACT_COMPONENT_MAP: dict[str, tuple[ComponentName, ...]] = {
    "identity_trust": (ComponentName.IDENTITY,),
    "device_trust": (ComponentName.DEVICE,),
    "runtime_trust": (ComponentName.RUNTIME,),
    "behaviour_trust": (ComponentName.BEHAVIOUR,),
    "network_trust": (ComponentName.NETWORK,),
    "geo_trust": (ComponentName.GEO,),
    "graph_trust": (ComponentName.GRAPH,),
    "transaction_trust": (ComponentName.TRANSACTION,),
    "session_trust": (ComponentName.THREAT,),
    "overall_trust": (ComponentName.THREAT,),
}

SEVERITY_THREAT_IMPACT = {
    "LOW": -5.0,
    "MEDIUM": -10.0,
    "HIGH": -18.0,
    "CRITICAL": -28.0,
}
