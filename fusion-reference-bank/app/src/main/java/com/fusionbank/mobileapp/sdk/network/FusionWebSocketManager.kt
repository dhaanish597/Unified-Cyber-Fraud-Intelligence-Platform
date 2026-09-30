package com.fusionbank.mobileapp.sdk.network

import android.util.Log
import com.fusionbank.mobileapp.sdk.models.FusionConnectionState
import com.fusionbank.mobileapp.sdk.models.SDKTrustUpdateEnvelope
import com.google.gson.Gson
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import okhttp3.*
import java.util.concurrent.TimeUnit

class FusionWebSocketManager(
    private val wsUrl: String,
    private val accessTokenProvider: () -> String?
) {
    private val TAG = "FusionWebSocketManager"
    private var client: OkHttpClient? = null
    private var webSocket: WebSocket? = null

    private val _connectionState = MutableStateFlow(FusionConnectionState.DISCONNECTED)
    val connectionState: StateFlow<FusionConnectionState> = _connectionState.asStateFlow()

    private val _lastMessage = MutableStateFlow<String?>(null)
    val lastMessage: StateFlow<String?> = _lastMessage.asStateFlow()

    private val _trustUpdates = MutableStateFlow<SDKTrustUpdateEnvelope?>(null)
    val trustUpdates: StateFlow<SDKTrustUpdateEnvelope?> = _trustUpdates.asStateFlow()

    private var scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var reconnectAttempt = 0
    private var reconnectJob: Job? = null
    private var isIntentionallyClosed = false
    private var activeSessionId: String? = null
    private val gson = Gson()

    private companion object {
        const val MAX_RECONNECT_ATTEMPTS = 5
    }

    fun connect(sessionId: String) {
        if (_connectionState.value == FusionConnectionState.CONNECTED) return

        activeSessionId = sessionId
        isIntentionallyClosed = false
        reconnectJob?.cancel()
        _connectionState.value = FusionConnectionState.SYNCING

        client = OkHttpClient.Builder()
            .readTimeout(0, TimeUnit.MILLISECONDS)
            .pingInterval(10, TimeUnit.SECONDS)
            .build()

        val scopedUrl = "$wsUrl${if (wsUrl.contains("?")) "&" else "?"}session_id=$sessionId"
        val request = Request.Builder()
            .url(scopedUrl)
            .apply {
                accessTokenProvider()?.takeIf { it.isNotBlank() }?.let {
                    header("Sec-WebSocket-Protocol", "Bearer.$it")
                }
            }
            .build()

        webSocket = client?.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                Log.d(TAG, "WebSocket connected successfully to $wsUrl")
                _connectionState.value = FusionConnectionState.CONNECTED
                reconnectAttempt = 0
                reconnectJob?.cancel()
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                _lastMessage.value = text
                try {
                    val update = gson.fromJson(text, SDKTrustUpdateEnvelope::class.java)
                    if (update.messageType == "trust_passport_update") {
                        _trustUpdates.value = update
                    }
                } catch (exception: Exception) {
                    Log.w(TAG, "Ignored unsupported WebSocket frame: ${exception.message}")
                }
            }

            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                Log.d(TAG, "WebSocket closing: $reason")
                _connectionState.value = FusionConnectionState.DISCONNECTED
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                Log.d(TAG, "WebSocket closed: $reason")
                _connectionState.value = FusionConnectionState.DISCONNECTED
                if (!isIntentionallyClosed) {
                    scheduleReconnect()
                }
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                Log.e(TAG, "WebSocket failure: ${t.message}")
                _connectionState.value = FusionConnectionState.DISCONNECTED
                if (!isIntentionallyClosed) {
                    scheduleReconnect()
                }
            }
        })
    }

    private fun scheduleReconnect() {
        if (isIntentionallyClosed) return
        if (reconnectJob?.isActive == true) return
        if (reconnectAttempt >= MAX_RECONNECT_ATTEMPTS) {
            Log.w(TAG, "WebSocket reconnect limit reached; user action is required")
            return
        }

        reconnectAttempt++
        val delayMs = (1000L * (1L shl (reconnectAttempt - 1).coerceAtMost(4))).coerceAtMost(16000L)
        Log.d(TAG, "Scheduling reconnect attempt #$reconnectAttempt in ${delayMs}ms")
        
        reconnectJob = scope.launch {
            delay(delayMs)
            if (!isIntentionallyClosed && _connectionState.value != FusionConnectionState.CONNECTED) {
                activeSessionId?.let(::connect)
            }
        }
    }

    fun disconnect() {
        isIntentionallyClosed = true
        reconnectJob?.cancel()
        reconnectJob = null
        reconnectAttempt = 0
        webSocket?.close(1000, "Client initiated disconnect")
        webSocket = null
        activeSessionId = null
        _connectionState.value = FusionConnectionState.DISCONNECTED
    }
}
