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
import kotlinx.coroutines.flow.first
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.UUID
import org.json.JSONObject
import android.os.Build
import android.os.BatteryManager
import android.app.ActivityManager
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.view.KeyEvent
import android.view.MotionEvent

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
    private lateinit var appContext: Context
    private var behaviorCollector: BehaviorBiometricsCollector? = null
    private var telemetryJob: Job? = null
    @Volatile private var accessToken: String? = null
    @Volatile private var accessTokenExpiresAt: Long = 0L
    @Volatile private var bankingAccessToken: String? = null
    @Volatile private var bankingAccessTokenExpiresAt: Long = 0L

    private val _activeSession = MutableStateFlow<SDKSessionResponse?>(null)
    val activeSession: StateFlow<SDKSessionResponse?> = _activeSession.asStateFlow()
    private val _bankingProfile = MutableStateFlow<BankingProfile?>(null)
    val bankingProfile: StateFlow<BankingProfile?> = _bankingProfile.asStateFlow()
    private val _lastLoginSecurity = MutableStateFlow<LoginSecurityAssessment?>(null)
    val lastLoginSecurity: StateFlow<LoginSecurityAssessment?> = _lastLoginSecurity.asStateFlow()
    private val _trustPassport = MutableStateFlow<SDKTrustPassportResponse?>(null)
    val trustPassport: StateFlow<SDKTrustPassportResponse?> = _trustPassport.asStateFlow()
    private val _trustHistory = MutableStateFlow<List<SDKTrustSnapshot>>(emptyList())
    val trustHistory: StateFlow<List<SDKTrustSnapshot>> = _trustHistory.asStateFlow()
    private val _trustDeltas = MutableStateFlow<List<SDKTrustDelta>>(emptyList())
    val trustDeltas: StateFlow<List<SDKTrustDelta>> = _trustDeltas.asStateFlow()
    private val _connectionState = MutableStateFlow(FusionConnectionState.DISCONNECTED)
    val connectionState: StateFlow<FusionConnectionState> = _connectionState.asStateFlow()
    private val _sdkLatencyMs = MutableStateFlow<Float?>(null)
    val sdkLatencyMs: StateFlow<Float?> = _sdkLatencyMs.asStateFlow()

    fun initialize(context: Context, customConfig: FusionConfig = FusionConfig()) {
        if (isInitialized) return
        appContext = context.applicationContext
        config = customConfig
        secureStorage = SecureStorage(context)
        accessToken = customConfig.accessToken
            ?: secureStorage.getString(SecureStorage.KEY_SDK_ACCESS_TOKEN)
            ?: secureStorage.getString(SecureStorage.KEY_ACCESS_TOKEN)
        accessTokenExpiresAt = secureStorage
            .getString(SecureStorage.KEY_SDK_ACCESS_EXPIRES_AT)?.toLongOrNull()
            ?: secureStorage.getString(SecureStorage.KEY_ACCESS_EXPIRES_AT)?.toLongOrNull() ?: 0L
        bankingAccessToken = secureStorage.getString(SecureStorage.KEY_BANKING_ACCESS_TOKEN)
        bankingAccessTokenExpiresAt = secureStorage
            .getString(SecureStorage.KEY_BANKING_ACCESS_EXPIRES_AT)?.toLongOrNull() ?: 0L

        val logging = HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BASIC
            else HttpLoggingInterceptor.Level.NONE
        }
        val okHttpClient = OkHttpClient.Builder()
            .addInterceptor { chain ->
                val builder = chain.request().newBuilder()
                val path = chain.request().url.encodedPath
                val token = if (path.startsWith("/banking/")) bankingAccessToken else accessToken
                token?.takeIf { it.isNotBlank() }?.let {
                    builder.header("Authorization", "Bearer $it")
                }
                if (::attestationEngine.isInitialized) {
                    builder.header("X-Fusion-VPN-Detected", attestationEngine.isVpnActive().toString())
                }
                chain.proceed(builder.build())
            }
            .addInterceptor(logging)
            .build()
        apiService = Retrofit.Builder()
            .baseUrl(config.baseUrl)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(FusionApiService::class.java)
        webSocketManager = FusionWebSocketManager(config.wsUrl) { accessToken }
        attestationEngine = DeviceAttestationEngine(context)
        queueManager = OfflineEventQueueManager(
            AppDatabase.getDatabase(context).eventDao(),
            apiService,
        )
        scope.launch {
            webSocketManager.connectionState.collect { state ->
                _connectionState.value = state
                if (state == FusionConnectionState.CONNECTED) queueManager.flushQueue()
            }
        }
        isInitialized = true
        Log.i(TAG, "Fusion SDK initialized: ${config.sdkVersion}")
    }

    fun analyzeSafeCheck(payload: String, onResult: (Result<SafeCheckResponse>) -> Unit) {
        checkInitialized()
        scope.launch {
            try {
                val response = apiService.analyzeSafeCheck(
                    SafeCheckAnalyzeRequest(payload, config.appId, BuildConfig.VERSION_NAME)
                )
                val body = response.body()
                if (!response.isSuccessful || body == null) {
                    throw backendError("SafeCheck assessment", response.code())
                }
                deliver(onResult, Result.success(body))
            } catch (exception: Exception) {
                deliver(onResult, Result.failure(exception))
            }
        }
    }

    fun reportSafeCheck(
        identifier: String,
        category: String,
        description: String,
        onResult: (Result<SafeCheckReportResponse>) -> Unit,
    ) {
        checkInitialized()
        scope.launch {
            try {
                val response = apiService.reportPaymentIdentifier(
                    SafeCheckReportRequest(identifier, category, description)
                )
                val body = response.body()
                if (!response.isSuccessful || body == null) {
                    throw backendError("SafeCheck report", response.code())
                }
                deliver(onResult, Result.success(body))
            } catch (exception: Exception) {
                deliver(onResult, Result.failure(exception))
            }
        }
    }

    /** Configure a freshly installed APK from a Developer Portal pairing payload. */
    fun pair(context: Context, payload: String, onResult: (Result<PairingRegistrationResponse>) -> Unit) {
        scope.launch {
            try {
                val json = JSONObject(payload)
                val backend = json.getString("backend").trimEnd('/') + "/"
                val ws = json.getString("ws")
                val pairId = json.getString("pairId")
                val bootstrap = json.getString("bootstrapToken")
                val tenantId = json.optString("tenantId", BuildConfig.TENANT_ID)
                check(tenantId == BuildConfig.TENANT_ID) { "Pairing QR belongs to a different tenant" }
                val environment = json.optString(
                    "environment",
                    if (BuildConfig.DEBUG) "DEVELOPMENT" else "PRODUCTION",
                )
                isInitialized = false
                initialize(context, FusionConfig(
                    baseUrl = backend,
                    wsUrl = ws,
                    appId = "com.fusionbank.mobileapp",
                    tenantId = BuildConfig.TENANT_ID,
                    sdkVersion = BuildConfig.SDK_VERSION,
                    environment = environment
                ))
                val request = PairingRegistrationRequest(
                    pairId = pairId,
                    bootstrapToken = bootstrap,
                    deviceUuid = getOrCreateDeviceId(),
                    androidVersion = Build.VERSION.RELEASE ?: "unknown",
                    manufacturer = Build.MANUFACTURER,
                    model = Build.MODEL,
                    sdkVersion = BuildConfig.SDK_VERSION,
                    appVersion = BuildConfig.VERSION_NAME,
                    fingerprint = Build.FINGERPRINT,
                    tenantId = tenantId,
                    environment = environment,
                )
                val response = apiService.registerPairedDevice(request)
                val body = response.body()
                if (!response.isSuccessful || body == null) {
                    throw backendError("Pairing", response.code())
                }
                persistPairing(body)
                // QR pairing is the authentication bootstrap. Do not report
                // success until the backend has also accepted the SDK session
                // and the authenticated realtime connection is established.
                scope.launch {
                    try {
                        startSessionInternal(body.deviceId) { sessionResult ->
                            sessionResult.fold(
                                onSuccess = { scope.launch { deliver(onResult, Result.success(body)) } },
                                onFailure = { error -> scope.launch { deliver(onResult, Result.failure(error)) } },
                            )
                        }
                    } catch (exception: Exception) {
                        deliver(onResult, Result.failure(exception))
                    }
                }
            } catch (exception: Exception) {
                deliver(onResult, Result.failure(exception))
            }
        }
    }

    private fun persistPairing(pairing: PairingRegistrationResponse) {
        accessToken = pairing.accessToken
        accessTokenExpiresAt = pairing.expiresAt * 1000L
        secureStorage.saveString(SecureStorage.KEY_SDK_ACCESS_TOKEN, pairing.accessToken)
        secureStorage.saveString(SecureStorage.KEY_SDK_ACCESS_EXPIRES_AT, accessTokenExpiresAt.toString())
        secureStorage.saveString(SecureStorage.KEY_ACCESS_TOKEN, pairing.accessToken)
        secureStorage.saveString(SecureStorage.KEY_ACCESS_EXPIRES_AT, accessTokenExpiresAt.toString())
        secureStorage.saveString(SecureStorage.KEY_BACKEND_URL, pairing.backendUrl + "/")
        secureStorage.saveString(SecureStorage.KEY_WS_URL, pairing.wsUrl)
        secureStorage.saveString(SecureStorage.KEY_DEVICE_ID, pairing.deviceId)
    }

    fun login(
        username: String,
        password: String,
        onResult: (Result<SDKSessionResponse>) -> Unit,
    ) {
        checkInitialized()
        scope.launch {
            try {
                val response = apiService.bankingLogin(
                    BankingLoginRequest(username.trim(), password, getOrCreateDeviceId())
                )
                val auth = response.body()
                if (!response.isSuccessful || auth == null) {
                    throw backendError("Sign-in", response.code())
                }
                persistAuthentication(auth)
                _lastLoginSecurity.value = auth.security
                startSessionInternal(auth.profile.userId, onResult)
            } catch (exception: Exception) {
                deliver(onResult, Result.failure(exception))
            }
        }
    }

    fun registerCustomer(
        fullName: String,
        email: String,
        mobileNumber: String,
        password: String,
        onResult: (Result<IdentityRegistrationResponse>) -> Unit,
    ) {
        checkInitialized()
        scope.launch {
            try {
                val profile = attestationEngine.generateDeviceProfile(getOrCreateDeviceId())
                val response = apiService.registerIdentity(
                    IdentityRegistrationRequest(
                        fullName = fullName.trim(), email = email.trim(), mobileNumber = mobileNumber.trim(), password = password,
                        deviceUuid = profile.deviceId, deviceFingerprint = Build.FINGERPRINT,
                        deviceModel = profile.model, deviceManufacturer = profile.manufacturer,
                        androidVersion = profile.androidVersion, sdkVersion = config.sdkVersion, appVersion = BuildConfig.VERSION_NAME,
                    )
                )
                val body = response.body()
                if (!response.isSuccessful || body == null) throw backendError("Registration", response.code())
                deliver(onResult, Result.success(body))
            } catch (exception: Exception) {
                deliver(onResult, Result.failure(exception))
            }
        }
    }

    fun restoreSession(onResult: (Result<SDKSessionResponse>) -> Unit) {
        checkInitialized()
        scope.launch {
            try {
                refreshBankingAuthentication()
                val userId = _bankingProfile.value?.userId
                    ?: secureStorage.getString(SecureStorage.KEY_USER_ID)
                    ?: throw IllegalStateException("Persistent session has no user identity")
                startSessionInternal(userId, onResult)
            } catch (exception: Exception) {
                clearLocalSession()
                deliver(onResult, Result.failure(exception))
            }
        }
    }

    /** Restore a QR-paired SDK session without requiring a banking password. */
    fun restorePairedSession(onResult: (Result<SDKSessionResponse>) -> Unit) {
        checkInitialized()
        scope.launch {
            try {
                ensureValidAccessToken()
                val deviceId = secureStorage.getString(SecureStorage.KEY_DEVICE_ID)
                    ?: throw IllegalStateException("No paired device")
                startSessionInternal(deviceId, onResult)
            } catch (exception: Exception) {
                clearLocalSession()
                deliver(onResult, Result.failure(exception))
            }
        }
    }

    @Deprecated("Use login() so banking identity is authenticated before SDK session creation")
    fun startSession(userId: String, onResult: (Result<SDKSessionResponse>) -> Unit) {
        checkInitialized()
        scope.launch {
            try {
                ensureValidAccessToken()
                startSessionInternal(userId, onResult)
            } catch (exception: Exception) {
                deliver(onResult, Result.failure(exception))
            }
        }
    }

    private suspend fun startSessionInternal(
        userId: String,
        onResult: (Result<SDKSessionResponse>) -> Unit,
    ) {
        val started = System.currentTimeMillis()
        ensureValidAccessToken()
        val deviceId = getOrCreateDeviceId()
        val deviceResponse = apiService.registerDevice(
            attestationEngine.generateDeviceProfile(deviceId)
        )
        if (!deviceResponse.isSuccessful) {
            return deliver(
                onResult,
                Result.failure(IllegalStateException("Device registration failed: HTTP ${deviceResponse.code()}")),
            )
        }
        val response = apiService.startSession(
            SDKSessionStartRequest(
                appId = config.appId,
                tenantId = config.tenantId,
                sdkVersion = config.sdkVersion,
                userId = userId,
                deviceId = deviceId,
                environment = config.environment,
            )
        )
        val session = response.body()
        if (!response.isSuccessful || session == null || !session.backendAck) {
            return deliver(
                onResult,
                Result.failure(backendError("Session start", response.code())),
            )
        }
                _activeSession.value = session
        secureStorage.saveString(SecureStorage.KEY_SESSION_ID, session.sessionId)
        secureStorage.saveString(SecureStorage.KEY_USER_ID, userId)
        _sdkLatencyMs.value = (System.currentTimeMillis() - started).toFloat()
        webSocketManager.connect(session.sessionId)
        withTimeout(15_000L) {
            connectionState.first { it == FusionConnectionState.CONNECTED }
        }
        startBehaviorCollection(appContext)
        startTelemetryLoop(appContext)
        reportEvent("SESSION_STARTED")
        deliver(onResult, Result.success(session))
    }

    fun reportEvent(
        eventType: String,
        amount: Double = 0.0,
        onResult: ((Result<SDKEventResponse>) -> Unit)? = null,
    ) {
        checkInitialized()
        val session = _activeSession.value
        val sessionId = session?.sessionId
            ?: secureStorage.getString(SecureStorage.KEY_SESSION_ID)
        if (sessionId == null) {
            onResult?.invoke(Result.failure(IllegalStateException("No active session")))
            return
        }
        val deviceId = session?.deviceId
            ?: secureStorage.getString(SecureStorage.KEY_DEVICE_ID)
        if (deviceId == null) {
            onResult?.invoke(Result.failure(IllegalStateException("No registered device")))
            return
        }
        val request = SDKEventRequest(
            sessionId = sessionId,
            deviceId = deviceId,
            eventType = eventType,
            amount = amount,
            sdkVersion = config.sdkVersion,
            requestId = newId("REQ"),
            correlationId = newId("COR"),
        )
        scope.launch {
            val started = System.currentTimeMillis()
            try {
                ensureValidAccessToken()
                val response = apiService.reportEvent(request)
                val acknowledgement = response.body()
                if (!response.isSuccessful || acknowledgement == null || !acknowledgement.backendAck) {
                    throw IllegalStateException("Event rejected: HTTP ${response.code()}")
                }
                _sdkLatencyMs.value = (System.currentTimeMillis() - started).toFloat()
                if (onResult != null) deliver(onResult, Result.success(acknowledgement))
            } catch (exception: Exception) {
                queueManager.enqueueEvent(request)
                if (onResult != null) deliver(onResult, Result.failure(exception))
            }
        }
    }

    fun requestDecision(
        eventType: String,
        amount: Double,
        beneficiaryId: String? = null,
        onResult: (Result<SDKDecisionResponse>) -> Unit,
    ) {
        checkInitialized()
        val sessionId = _activeSession.value?.sessionId
            ?: return onResult(Result.failure(IllegalStateException("No active session")))
        val request = SDKDecisionRequest(
            sessionId = sessionId,
            eventType = eventType,
            amount = amount,
            beneficiaryId = beneficiaryId,
            requestId = newId("REQ"),
            correlationId = newId("COR"),
        )
        scope.launch {
            val started = System.currentTimeMillis()
            try {
                ensureValidAccessToken()
                val response = apiService.requestDecision(request)
                val decision = response.body()
                if (!response.isSuccessful || decision == null || !decision.backendAck) {
                    throw IllegalStateException("Decision failed: HTTP ${response.code()}")
                }
                _sdkLatencyMs.value = (System.currentTimeMillis() - started).toFloat()
                deliver(onResult, Result.success(decision))
            } catch (exception: Exception) {
                deliver(onResult, Result.failure(exception))
            }
        }
    }

    fun getTrustPassport(onResult: (Result<SDKTrustPassportResponse>) -> Unit) {
        val sessionId = _activeSession.value?.sessionId
            ?: return onResult(Result.failure(IllegalStateException("No active session")))
        scope.launch {
            try {
                ensureValidAccessToken()
                val response = apiService.getTrustPassport(sessionId)
                val passport = response.body()
                if (!response.isSuccessful || passport == null) {
                    throw IllegalStateException("Trust data unavailable: HTTP ${response.code()}")
                }
                _trustPassport.value = passport
                deliver(onResult, Result.success(passport))
            } catch (exception: Exception) {
                deliver(onResult, Result.failure(exception))
            }
        }
    }

    fun refreshTrustHistory(range: String = "last_hour") {
        val sessionId = _activeSession.value?.sessionId ?: return
        scope.launch {
            try {
                ensureValidAccessToken()
                val response = apiService.getTrustHistory(sessionId, range)
                if (response.isSuccessful) _trustHistory.value = response.body()?.snapshots.orEmpty()
            } catch (exception: Exception) {
                Log.w(TAG, "Trust history unavailable: ${exception.message}")
            }
        }
    }

    fun logout(onResult: (Result<Unit>) -> Unit) {
        if (!isInitialized) return onResult(Result.success(Unit))
        scope.launch {
            val refreshToken = secureStorage.getString(SecureStorage.KEY_BANKING_REFRESH_TOKEN)
            try {
                ensureValidBankingToken()
                reportEvent("USER_LOGOUT")
                val response = apiService.bankingLogout(BankingLogoutRequest(refreshToken))
                if (!response.isSuccessful && response.code() != 401) {
                    throw IllegalStateException("Logout failed: HTTP ${response.code()}")
                }
                clearLocalSession()
                deliver(onResult, Result.success(Unit))
            } catch (exception: Exception) {
                clearLocalSession()
                deliver(onResult, Result.failure(exception))
            }
        }
    }

    fun endSession() {
        if (!isInitialized) return
        if (_activeSession.value != null) reportEvent("SESSION_ENDED")
        clearLocalSession()
    }

    /** Privacy-safe lifecycle signal; no screen contents or input values are sent. */
    fun reportLifecycleEvent(eventType: String) {
        if (_activeSession.value != null) reportEvent(eventType)
    }

    fun shutdown() {
        endSession()
        isInitialized = false
    }

    fun setAccessToken(token: String) {
        require(token.isNotBlank())
        accessToken = token
        accessTokenExpiresAt = Long.MAX_VALUE
    }

    private suspend fun ensureValidAccessToken() {
        val now = System.currentTimeMillis() / 1000L
        if (!accessToken.isNullOrBlank() && accessTokenExpiresAt > now + 30L) return
        val clientId = config.developmentClientId
        val clientSecret = config.developmentClientSecret
        if (clientId.isNullOrBlank() || clientSecret.isNullOrBlank()) {
            throw IllegalStateException("No valid banking or platform access token")
        }
        check(BuildConfig.DEBUG) { "Embedded client credentials are forbidden in release builds" }
        val response = apiService.createAccessToken(SDKTokenRequest(clientId, clientSecret))
        val token = response.body()
        if (!response.isSuccessful || token == null) {
            throw IllegalStateException("Development authentication failed: HTTP ${response.code()}")
        }
        accessToken = token.accessToken
        accessTokenExpiresAt = token.expiresAt
    }

    private suspend fun ensureValidBankingToken() {
        val now = System.currentTimeMillis() / 1000L
        if (!bankingAccessToken.isNullOrBlank() && bankingAccessTokenExpiresAt > now + 30L) return
        if (secureStorage.getString(SecureStorage.KEY_BANKING_REFRESH_TOKEN).isNullOrBlank()) {
            throw IllegalStateException("No valid banking session")
        }
        refreshBankingAuthentication()
    }

    private suspend fun refreshBankingAuthentication() {
        val refreshToken = secureStorage.getString(SecureStorage.KEY_BANKING_REFRESH_TOKEN)
            ?: throw IllegalStateException("No persistent banking session")
        val response = apiService.refreshBankingToken(
            BankingRefreshRequest(refreshToken, getOrCreateDeviceId())
        )
        val auth = response.body()
        if (!response.isSuccessful || auth == null) {
            throw IllegalStateException("Banking session expired")
        }
        persistAuthentication(auth)
    }

    private fun persistAuthentication(auth: BankingAuthResponse) {
        bankingAccessToken = auth.accessToken
        bankingAccessTokenExpiresAt = auth.expiresAt
        _bankingProfile.value = auth.profile
        secureStorage.saveString(SecureStorage.KEY_BANKING_ACCESS_TOKEN, auth.accessToken)
        secureStorage.saveString(SecureStorage.KEY_BANKING_ACCESS_EXPIRES_AT, auth.expiresAt.toString())
        secureStorage.saveString(SecureStorage.KEY_BANKING_REFRESH_TOKEN, auth.refreshToken)
        secureStorage.saveString(SecureStorage.KEY_REFRESH_EXPIRES_AT, auth.refreshExpiresAt.toString())
        secureStorage.saveString(SecureStorage.KEY_USER_ID, auth.profile.userId)
    }

    private fun getOrCreateDeviceId(): String {
        secureStorage.getString(SecureStorage.KEY_DEVICE_ID)?.takeIf { it.isNotBlank() }?.let {
            return it
        }
        val created = "DEV_${UUID.randomUUID().toString().substring(0, 8).uppercase()}"
        secureStorage.saveString(SecureStorage.KEY_DEVICE_ID, created)
        return created
    }

    fun startBehaviorCollection(context: Context) {
        val session = _activeSession.value ?: return
        if (behaviorCollector != null) return
        Log.i(TAG, "Starting behavioral biometrics collection for session: ${session.sessionId}")
        behaviorCollector = BehaviorBiometricsCollector(
            context = context.applicationContext,
            scope = scope,
            onFlush = { payload ->
                try {
                    ensureValidAccessToken()
                    val response = apiService.reportBehavioralBiometrics(payload)
                    if (response.isSuccessful) {
                        val ack = response.body()
                        if (ack != null) {
                            val trust = ack.behaviourTrust
                            if (trust != null) {
                                withContext(Dispatchers.Main) {
                                    _activeSession.value?.let { currentSession ->
                                        _activeSession.value = currentSession.copy(behaviourTrust = trust)
                                    }
                                }
                            }
                        }
                    } else {
                        Log.w(TAG, "Failed to send behavioral biometrics: HTTP ${response.code()}")
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Error sending behavioral biometrics", e)
                }
            }
        ).apply {
            start(session.sessionId, session.deviceId)
        }
    }

    fun stopBehaviorCollection() {
        Log.i(TAG, "Stopping behavioral biometrics collection")
        behaviorCollector?.stop()
        behaviorCollector = null
    }

    fun dispatchTouchEvent(event: MotionEvent) {
        behaviorCollector?.onTouchEvent(event)
    }

    fun dispatchKeyEvent(event: KeyEvent): Boolean {
        return behaviorCollector?.onKeyEvent(event) ?: false
    }

    fun startTelemetryLoop(context: Context) {
        val session = _activeSession.value ?: return
        if (telemetryJob != null) return
        Log.i(TAG, "Starting continuous cyber telemetry loop (1s interval) for session: ${session.sessionId}")
        
        telemetryJob = scope.launch(Dispatchers.IO) {
            val deviceId = session.deviceId
            val activityManager = appContext.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
            val batteryManager = appContext.getSystemService(Context.BATTERY_SERVICE) as BatteryManager

            while (isActive) {
                try {
                    val memory = ActivityManager.MemoryInfo().also { activityManager.getMemoryInfo(it) }
                    val memoryUsage = if (memory.totalMem > 0) {
                        ((memory.totalMem - memory.availMem).toDouble() / memory.totalMem * 100.0).toFloat()
                    } else 0f
                    val battery = batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
                        .coerceIn(0, 100).toFloat()
                    val vpn = attestationEngine.isVpnActive()
                    
                    val request = SDKTelemetryRequest(
                        sessionId = session.sessionId,
                        deviceId = deviceId,
                        cpuUsage = 0f,
                        memoryUsage = memoryUsage,
                        batteryLevel = battery,
                        foregroundApp = appContext.packageName,
                        networkType = readNetworkType(),
                        vpnActive = vpn,
                        proxyActive = attestationEngine.checkProxy(),
                        location = "",
                        rootDetected = attestationEngine.checkRoot(),
                        debuggerAttached = android.os.Debug.isDebuggerConnected(),
                        fridaDetected = attestationEngine.checkFrida(),
                        magiskDetected = attestationEngine.checkMagisk(),
                        emulatorDetected = attestationEngine.checkEmulator(),
                        accessibilityActive = attestationEngine.checkAccessibility(),
                        overlayActive = attestationEngine.checkOverlay(),
                        mitmActive = attestationEngine.checkMitm(),
                        sslPinningOk = attestationEngine.checkSslPinning(),
                        appSignatureOk = attestationEngine.checkAppSignature(),
                        apkTampered = attestationEngine.checkApkTampering(),
                        screenCaptureActive = attestationEngine.checkScreenCapture(),
                        developerOptionsActive = attestationEngine.checkDeveloperOptions(),
                        capturedAt = System.currentTimeMillis()
                    )
                    
                    ensureValidAccessToken()
                    val response = apiService.reportTelemetry(request)
                    if (!response.isSuccessful) {
                        Log.w(TAG, "Telemetry send failure: HTTP ${response.code()}")
                    }
                } catch (e: CancellationException) {
                    throw e
                } catch (e: Exception) {
                    Log.w(TAG, "Error in telemetry streaming loop: ${e.message}")
                }
                delay(1000L)
            }
        }
    }

    private fun readNetworkType(): String {
        val manager = appContext.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = manager.activeNetwork ?: return "OFFLINE"
        val capabilities = manager.getNetworkCapabilities(network) ?: return "UNKNOWN"
        return when {
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "WIFI"
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> "CELLULAR"
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_VPN) -> "VPN"
            else -> "OTHER"
        }
    }

    fun stopTelemetryLoop() {
        Log.i(TAG, "Stopping continuous cyber telemetry loop")
        telemetryJob?.cancel()
        telemetryJob = null
    }

    private fun clearLocalSession() {
        stopBehaviorCollection()
        stopTelemetryLoop()
        webSocketManager.disconnect()
        _activeSession.value = null
        _bankingProfile.value = null
        _trustPassport.value = null
        _trustHistory.value = emptyList()
        _trustDeltas.value = emptyList()
        _sdkLatencyMs.value = null
        accessToken = null
        accessTokenExpiresAt = 0L
        bankingAccessToken = null
        bankingAccessTokenExpiresAt = 0L
        secureStorage.clearSessionPreservingDevice()
    }

    private fun newId(prefix: String): String =
        "${prefix}_${UUID.randomUUID().toString().replace("-", "").uppercase()}"

    private fun backendError(operation: String, status: Int): IllegalStateException =
        IllegalStateException(
            when (status) {
                401 -> "$operation could not be completed. The session is not authorized; pair this device again and retry."
                403 -> "$operation is not available for this device. Pair it again from the Developer Portal."
                503 -> "$operation service is temporarily unavailable. Keep this pairing screen open and retry in a moment."
                else -> "$operation could not be completed. Check the pairing payload and retry."
            }
        )

    private suspend fun <T> deliver(callback: (Result<T>) -> Unit, result: Result<T>) {
        withContext(Dispatchers.Main) { callback(result) }
    }

    fun getBaseUrl(): String = if (isInitialized) config.baseUrl else BuildConfig.FUSION_BASE_URL

    private fun checkInitialized() {
        check(isInitialized) { "Fusion SDK is not initialized" }
    }
}
