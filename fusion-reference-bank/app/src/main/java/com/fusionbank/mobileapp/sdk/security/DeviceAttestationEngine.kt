package com.fusionbank.mobileapp.sdk.security

import android.content.Context
import android.os.Build
import android.os.Debug
import com.fusionbank.mobileapp.sdk.models.SDKDeviceRequest
import java.io.File
import java.util.*

class DeviceAttestationEngine(private val context: Context) {

    fun generateDeviceProfile(deviceId: String): SDKDeviceRequest {
        val rootDetected = checkRoot()
        val emulatorDetected = checkEmulator()
        val fridaDetected = checkFrida()
        val debuggerAttached = Debug.isDebuggerConnected() || Debug.waitingForDebugger()
        val overlayDetected = false // System overlay check

        return SDKDeviceRequest(
            deviceId = deviceId,
            model = Build.MODEL ?: "Android Device",
            manufacturer = Build.MANUFACTURER ?: "Generic",
            androidVersion = Build.VERSION.RELEASE ?: "14",
            securityPatch = Build.VERSION.SECURITY_PATCH ?: "2026-07-01",
            screenLockEnabled = true,
            rootDetected = rootDetected,
            emulatorDetected = emulatorDetected,
            fridaDetected = fridaDetected,
            debuggerAttached = debuggerAttached,
            overlayDetected = overlayDetected,
            timezone = TimeZone.getDefault().id ?: "Asia/Kolkata",
            locale = Locale.getDefault().toString()
        )
    }

    private fun checkRoot(): Boolean {
        val paths = arrayOf(
            "/system/app/Superuser.apk",
            "/sbin/su",
            "/system/bin/su",
            "/system/xbin/su",
            "/data/local/xbin/su",
            "/data/local/bin/su",
            "/system/sd/xbin/su",
            "/system/bin/failsafe/su",
            "/data/local/su"
        )
        for (path in paths) {
            if (File(path).exists()) return true
        }
        return false
    }

    private fun checkEmulator(): Boolean {
        return (Build.FINGERPRINT.startsWith("generic")
                || Build.FINGERPRINT.startsWith("unknown")
                || Build.MODEL.contains("google_sdk")
                || Build.MODEL.contains("Emulator")
                || Build.MODEL.contains("Android SDK built for x86")
                || Build.MANUFACTURER.contains("Genymotion")
                || Build.BRAND.startsWith("generic") && Build.DEVICE.startsWith("generic")
                || "google_sdk" == Build.PRODUCT)
    }

    private fun checkFrida(): Boolean {
        // Simple port check or process check placeholder
        return false
    }
}
