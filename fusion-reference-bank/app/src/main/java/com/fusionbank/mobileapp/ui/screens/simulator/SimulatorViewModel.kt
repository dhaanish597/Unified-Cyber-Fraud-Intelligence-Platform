package com.fusionbank.mobileapp.ui.screens.simulator

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.fusionbank.mobileapp.sdk.Fusion
import com.fusionbank.mobileapp.sdk.models.SDKDecisionResponse
import com.fusionbank.mobileapp.sdk.models.SDKTrustPassportResponse
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import javax.inject.Inject

data class LiveLogEntry(
    val timestamp: String,
    val eventName: String,
    val category: String,
    val status: String,
    val latencyMs: Long,
    val details: String = ""
)

@HiltViewModel
class SimulatorViewModel @Inject constructor() : ViewModel() {

    // Section 2: Device Security Toggles
    val rootDetected = MutableStateFlow(false)
    val magiskDetected = MutableStateFlow(false)
    val bootloaderUnlocked = MutableStateFlow(false)
    val usbDebugging = MutableStateFlow(false)
    val devOptions = MutableStateFlow(false)
    val unknownSources = MutableStateFlow(false)
    val emulatorDetected = MutableStateFlow(false)
    val appIntegrityFailure = MutableStateFlow(false)

    // Section 3: Runtime Integrity Toggles
    val debuggerAttached = MutableStateFlow(false)
    val fridaDetected = MutableStateFlow(false)
    val xposedDetected = MutableStateFlow(false)
    val runtimeHooking = MutableStateFlow(false)
    val memoryTampering = MutableStateFlow(false)
    val codeInjection = MutableStateFlow(false)
    val nativeLibModified = MutableStateFlow(false)
    val certPinningFailure = MutableStateFlow(false)

    // Section 4: Overlay Attack Toggles
    val overlayAttack = MutableStateFlow(false)
    val accessibilityAbuse = MutableStateFlow(false)
    val screenRecording = MutableStateFlow(false)
    val screenshotAttempt = MutableStateFlow(false)
    val tapInjection = MutableStateFlow(false)
    val clickHijacking = MutableStateFlow(false)

    // Section 5: Network Threat Toggles
    val vpnEnabled = MutableStateFlow(false)
    val torEnabled = MutableStateFlow(false)
    val proxyEnabled = MutableStateFlow(false)
    val publicWifi = MutableStateFlow(false)
    val mitmSimulation = MutableStateFlow(false)
    val sslDowngrade = MutableStateFlow(false)
    val ipReputationLow = MutableStateFlow(false)

    // Section 7: Behaviour Sliders
    val typingSpeed = MutableStateFlow(0.5f)
    val touchPressure = MutableStateFlow(0.5f)
    val navigationSpeed = MutableStateFlow(0.5f)
    val transactionUrgency = MutableStateFlow(0.5f)

    // Section 7: Behaviour Toggles
    val roboticBehaviour = MutableStateFlow(false)
    val unusualNavigation = MutableStateFlow(false)
    val fastTransfer = MutableStateFlow(false)
    val repeatedOtpAttempts = MutableStateFlow(false)

    // Live Telemetry Streams & Logs
    private val _eventLogs = MutableStateFlow<List<LiveLogEntry>>(emptyList())
    val eventLogs: StateFlow<List<LiveLogEntry>> = _eventLogs.asStateFlow()

    private val _developerLogs = MutableStateFlow<List<String>>(emptyList())
    val developerLogs: StateFlow<List<String>> = _developerLogs.asStateFlow()

    private val _latestDecision = MutableStateFlow<SDKDecisionResponse?>(null)
    val latestDecision: StateFlow<SDKDecisionResponse?> = _latestDecision.asStateFlow()

    private val _isCampaignRunning = MutableStateFlow(false)
    val isCampaignRunning: StateFlow<Boolean> = _isCampaignRunning.asStateFlow()

    private val dateFormat = SimpleDateFormat("HH:mm:ss.SSS", Locale.getDefault())

    init {
        addLog("SYSTEM_INIT", "SDK", "HEALTHY", 0, "Simulator initialized successfully")
        refreshPassport()
    }

    fun triggerEvent(eventName: String, amount: Double = 0.0, category: String = "SIMULATION") {
        val t0 = System.currentTimeMillis()
        Fusion.reportEvent(eventName, amount) { result ->
            val latency = System.currentTimeMillis() - t0
            result.onSuccess { acknowledgement ->
                addLog(eventName, category, "ACK 200", latency, "Backend event ${acknowledgement.eventId}")
                addDevLog("[Backend ACK] event_id=${acknowledgement.eventId}, event_type=$eventName, latency=${acknowledgement.ingestionLatencyMs}ms")
            }.onFailure { exception ->
                addLog(eventName, category, "QUEUED", latency, exception.message ?: "Delivery failed")
                addDevLog("[SDK QUEUE] event_type=$eventName, reason=${exception.message}")
            }
        }
    }

    fun triggerDecision(eventType: String, amount: Double) {
        viewModelScope.launch {
            val t0 = System.currentTimeMillis()
            addDevLog("[SDK -> POST /sdk/request-decision] event_type=$eventType, amount=$amount")
            Fusion.requestDecision(eventType, amount) { result ->
                val latency = System.currentTimeMillis() - t0
                result.onSuccess { decision ->
                    _latestDecision.value = decision
                    addLog(
                        "DECISION_RECEIVED",
                        "DECISION",
                        decision.decision,
                        latency,
                        "Verdict: ${decision.decision} (Confidence: ${decision.confidence}%)"
                    )
                    addDevLog("[Backend -> SDK] Decision: ${decision.decision}, Reasons: ${decision.reasonCodes.joinToString()}")
                }.onFailure { ex ->
                    addLog("DECISION_FAILED", "DECISION", "ERROR", latency, ex.message ?: "Failed")
                }
            }
            refreshPassport()
        }
    }

    fun runScenario(scenario: ThreatScenario) {
        if (_isCampaignRunning.value) return
        _isCampaignRunning.value = true

        viewModelScope.launch {
            addDevLog("=== STARTING CAMPAIGN: ${scenario.title} ===")
            addLog("CAMPAIGN_START", "CAMPAIGN", scenario.threatLevel, 0, "Executing ${scenario.title}")

            for (event in scenario.eventsToSimulate) {
                delay(event.delayMs)
                if (event.isDecisionRequest) {
                    triggerDecision(event.eventType, event.amount)
                } else {
                    triggerEvent(event.eventType, event.amount, "CAMPAIGN")
                }
            }

            _isCampaignRunning.value = false
            addLog("CAMPAIGN_COMPLETE", "CAMPAIGN", "SUCCESS", 0, "Campaign ${scenario.title} finished")
            addDevLog("=== CAMPAIGN COMPLETED: ${scenario.title} ===")
        }
    }

    fun refreshPassport() {
        Fusion.getTrustPassport { result ->
            result.onSuccess { passport ->
                addDevLog("[Backend -> Passport] Overall Trust: ${passport.overallTrust}, Version: ${passport.version}")
            }
        }
    }

    private fun addLog(eventName: String, category: String, status: String, latencyMs: Long, details: String) {
        val entry = LiveLogEntry(
            timestamp = dateFormat.format(Date()),
            eventName = eventName,
            category = category,
            status = status,
            latencyMs = latencyMs,
            details = details
        )
        _eventLogs.value = (listOf(entry) + _eventLogs.value).take(100)
    }

    private fun addDevLog(msg: String) {
        val timestamped = "[${dateFormat.format(Date())}] $msg"
        _developerLogs.value = (listOf(timestamped) + _developerLogs.value).take(150)
    }
}
