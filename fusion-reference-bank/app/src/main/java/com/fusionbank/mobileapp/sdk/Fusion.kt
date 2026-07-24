package com.fusionbank.mobileapp.sdk

import android.content.Context
import android.util.Log
import com.fusionbank.mobileapp.BuildConfig
import com.fusionbank.mobileapp.sdk.models.*
import com.fusionbank.mobileapp.sdk.network.FusionApiService
import com.fusionbank.mobileapp.sdk.network.FusionWebSocketManager
import com.fusionbank.mobileapp.sdk.queue.AppDatabase
import com.fusionbank.mobileapp.sdk.queue.OfflineEventQueueManager
import com.fusionbank.mobileapp.sdk.security.DeviceAttestationEngine
import com.fusionbank.mobileapp.sdk.security.SecureStorage
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.UUID

object Fusion {
    private const val TAG = "FusionSDK"

    private var isInitialized = false
    private var config = FusionConfig()
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    private lateinit var apiService: FusionApiService
    private lateinit var webSocketManager: FusionWebSocketManager
    private lateinit var secureStorage: SecureStorage
    private lateinit var attestationEngine: DeviceAttestationEngine
    private lateinit var queueManager: OfflineEventQueueManager

    private val _activeSession = MutableStateFlow<SDKSessionResponse?>(null)
    val activeSession: StateFlow<SDKSessionResponse?> = _activeSession.asStateFlow()

    private val _trustPassport = MutableStateFlow<SDKTrustPassportResponse?>(null)
    val trustPassport: StateFlow<SDKTrustPassportResponse?> = _trustPassport.asStateFlow()

    private val _trustHistory = MutableStateFlow<List<SDKTrustSnapshot>>(emptyList())
    val trustHistory: StateFlow<List<SDKTrustSnapshot>> = _trustHistory.asStateFlow()

    private val _trustDeltas = MutableStateFlow<List<SDKTrustDelta>>(emptyList())
    val trustDeltas: StateFlow<List<SDKTrustDelta>> = _trustDeltas.asStateFlow()

    private val _connectionState = MutableStateFlow(FusionConnectionState.DISCONNECTED)
    val connectionState: StateFlow<FusionConnectionState> = _connectionState.asStateFlow()

    private val _sdkLatencyMs = MutableStateFlow(12f)
    val sdkLatencyMs: StateFlow<Float> = _sdkLatencyMs.asStateFlow()

    fun initialize(context: Context, customConfig: FusionConfig = FusionConfig()) {
        if (isInitialized) return
        config = customConfig

        val logging = HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) {
                HttpLoggingInterceptor.Level.BASIC
            } else {
                HttpLoggingInterceptor.Level.NONE
            }
        }
        val okHttpClient = OkHttpClient.Builder()
            .addInterceptor(logging)
            .build()

        val retrofit = Retrofit.Builder()
            .baseUrl(config.baseUrl)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        apiService = retrofit.create(FusionApiService::class.java)
        webSocketManager = FusionWebSocketManager(config.wsUrl)
        secureStorage = SecureStorage(context)
        attestationEngine = DeviceAttestationEngine(context)

        val db = AppDatabase.getDatabase(context)
        queueManager = OfflineEventQueueManager(db.eventDao(), apiService)

        // Observe WebSocket state
        scope.launch {
            webSocketManager.connectionState.collect { state ->
                _connectionState.value = state
                if (state == FusionConnectionState.CONNECTED) {
                    queueManager.flushQueue()
                }
            }
        }

        scope.launch {
            webSocketManager.trustUpdates.collect { update ->
                if (update == null) return@collect
                _trustPassport.value = update.passport
                _sdkLatencyMs.value = update.processingTimeMs
                update.snapshot?.let { snapshot ->
                    _trustHistory.value = (_trustHistory.value + snapshot).takeLast(500)
                }
                if (update.deltas.isNotEmpty()) {
                    _trustDeltas.value = (update.deltas + _trustDeltas.value).take(200)
                }
            }
        }

        isInitialized = true
        Log.i(TAG, "Fusion Adaptive Trust SDK initialized successfully. Version: ${config.sdkVersion}")
    }

    fun startSession(userId: String, onResult: (Result<SDKSessionResponse>) -> Unit) {
        checkInitialized()
        scope.launch {
            val t0 = System.currentTimeMillis()
            var deviceId = secureStorage.getString(SecureStorage.KEY_DEVICE_ID)
            if (deviceId.isNullOrEmpty()) {
                deviceId = "DEV_${UUID.randomUUID().toString().substring(0, 8).uppercase()}"
                secureStorage.saveString(SecureStorage.KEY_DEVICE_ID, deviceId)
            }

            try {
                // Register Device
                val deviceReq = attestationEngine.generateDeviceProfile(deviceId)
                apiService.registerDevice(deviceReq)

                // Start SDK Session
                val sessionReq = SDKSessionStartRequest(
                    appId = config.appId,
                    tenantId = config.tenantId,
                    sdkVersion = config.sdkVersion,
                    userId = userId,
                    deviceId = deviceId,
                    environment = config.environment
                )
                val response = apiService.startSession(sessionReq)
                if (response.isSuccessful && response.body() != null) {
                    val session = response.body()!!
                    _activeSession.value = session
                    secureStorage.saveString(SecureStorage.KEY_SESSION_ID, session.sessionId)
                    secureStorage.saveString(SecureStorage.KEY_USER_ID, userId)
                    _sdkLatencyMs.value = (System.currentTimeMillis() - t0).toFloat()

                    // Connect WebSocket
                    webSocketManager.connect(session.sessionId)
                    refreshTrustHistory()

                    // Report initial SESSION_STARTED event
                    reportEvent("SESSION_STARTED")

                    withContext(Dispatchers.Main) {
                        onResult(Result.success(session))
                    }
                } else {
                    withContext(Dispatchers.Main) {
                        onResult(Result.failure(Exception("Session start failed: HTTP ${response.code()}")))
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error starting session: ${e.message}")
                withContext(Dispatchers.Main) {
                    onResult(Result.failure(e))
                }
            }
        }
    }

    fun reportEvent(
        eventType: String,
        amount: Double = 0.0,
        onResult: ((Result<SDKEventResponse>) -> Unit)? = null
    ) {
        checkInitialized()
        val session = _activeSession.value
        val sessionId = session?.sessionId ?: secureStorage.getString(SecureStorage.KEY_SESSION_ID) ?: "SDK_SESS_DEMO"
        val deviceId = session?.deviceId ?: secureStorage.getString(SecureStorage.KEY_DEVICE_ID) ?: "DEV_DEMO"
        val trust = session?.compositeTrustScore ?: 82.0f

        val request = SDKEventRequest(
            sessionId = sessionId,
            deviceId = deviceId,
            eventType = eventType,
            amount = amount,
            compositeTrust = trust,
            sdkVersion = config.sdkVersion
        )

        scope.launch {
            val t0 = System.currentTimeMillis()
            try {
                if (_connectionState.value == FusionConnectionState.DISCONNECTED) {
                    queueManager.enqueueEvent(request)
                    withContext(Dispatchers.Main) {
                        onResult?.invoke(Result.failure(Exception("Event queued for offline retry")))
                    }
                } else {
                    val response = apiService.reportEvent(request)
                    if (!response.isSuccessful) {
                        queueManager.enqueueEvent(request)
                        withContext(Dispatchers.Main) {
                            onResult?.invoke(Result.failure(Exception("Event rejected: HTTP ${response.code()}")))
                        }
                    } else {
                        _sdkLatencyMs.value = (System.currentTimeMillis() - t0).toFloat()
                        val acknowledgement = response.body()
                        withContext(Dispatchers.Main) {
                            if (acknowledgement != null) {
                                onResult?.invoke(Result.success(acknowledgement))
                            } else {
                                onResult?.invoke(Result.failure(Exception("Empty event acknowledgement")))
                            }
                        }
                    }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Network error during reportEvent, queuing offline: ${e.message}")
                queueManager.enqueueEvent(request)
                withContext(Dispatchers.Main) {
                    onResult?.invoke(Result.failure(e))
                }
            }
        }
    }

    fun requestDecision(
        eventType: String,
        amount: Double,
        onResult: (Result<SDKDecisionResponse>) -> Unit
    ) {
        checkInitialized()
        val session = _activeSession.value
        val sessionId = session?.sessionId ?: secureStorage.getString(SecureStorage.KEY_SESSION_ID) ?: "SDK_SESS_DEMO"
        val trust = session?.compositeTrustScore ?: 82.0f

        val request = SDKDecisionRequest(
            sessionId = sessionId,
            eventType = eventType,
            amount = amount,
            compositeTrust = trust,
            vpnDetected = false,
            rootDetected = false,
            runtimeTrust = 94.0f
        )

        scope.launch {
            val t0 = System.currentTimeMillis()
            try {
                val response = apiService.requestDecision(request)
                if (response.isSuccessful && response.body() != null) {
                    val decision = response.body()!!
                    _sdkLatencyMs.value = (System.currentTimeMillis() - t0).toFloat()
                    withContext(Dispatchers.Main) {
                        onResult(Result.success(decision))
                    }
                } else {
                    withContext(Dispatchers.Main) {
                        onResult(Result.failure(Exception("Decision failed: HTTP ${response.code()}")))
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Decision request error: ${e.message}")
                withContext(Dispatchers.Main) {
                    onResult(Result.failure(e))
                }
            }
        }
    }

    fun getTrustPassport(onResult: (Result<SDKTrustPassportResponse>) -> Unit) {
        checkInitialized()
        val sessionId = _activeSession.value?.sessionId ?: secureStorage.getString(SecureStorage.KEY_SESSION_ID) ?: "SDK_SESS_DEMO"
        scope.launch {
            try {
                val response = apiService.getTrustPassport(sessionId)
                if (response.isSuccessful && response.body() != null) {
                    val passport = response.body()!!
                    _trustPassport.value = passport
                    withContext(Dispatchers.Main) {
                        onResult(Result.success(passport))
                    }
                } else {
                    withContext(Dispatchers.Main) {
                        onResult(Result.failure(Exception("Passport request failed: HTTP ${response.code()}")))
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    onResult(Result.failure(e))
                }
            }
        }
    }

    fun refreshTrustHistory(range: String = "last_hour") {
        checkInitialized()
        val sessionId = _activeSession.value?.sessionId
            ?: secureStorage.getString(SecureStorage.KEY_SESSION_ID)
            ?: return
        scope.launch {
            try {
                val response = apiService.getTrustHistory(sessionId, range)
                if (response.isSuccessful) {
                    _trustHistory.value = response.body()?.snapshots.orEmpty()
                }
            } catch (exception: Exception) {
                Log.w(TAG, "Trust history synchronization failed: ${exception.message}")
            }
        }
    }

    fun endSession() {
        if (!isInitialized) return
        reportEvent("SESSION_ENDED")
        webSocketManager.disconnect()
        _activeSession.value = null
        _trustPassport.value = null
        _trustHistory.value = emptyList()
        _trustDeltas.value = emptyList()
        secureStorage.clearAll()
        Log.i(TAG, "Fusion session terminated.")
    }

    fun shutdown() {
        endSession()
        isInitialized = false
    }

    private fun checkInitialized() {
        if (!isInitialized) {
            throw IllegalStateException("Fusion SDK is not initialized. Call Fusion.initialize(context) first.")
        }
    }
}
