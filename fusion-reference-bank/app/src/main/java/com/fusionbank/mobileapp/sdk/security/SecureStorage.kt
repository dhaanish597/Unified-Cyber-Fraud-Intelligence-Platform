package com.fusionbank.mobileapp.sdk.security

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class SecureStorage(context: Context) {

    private val prefs: SharedPreferences = run {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()

        EncryptedSharedPreferences.create(
            context,
            "fusion_secure_prefs",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }

    fun saveString(key: String, value: String) {
        prefs.edit().putString(key, value).apply()
    }

    fun getString(key: String, defaultValue: String? = null): String? {
        return prefs.getString(key, defaultValue)
    }

    fun saveBoolean(key: String, value: Boolean) {
        prefs.edit().putBoolean(key, value).apply()
    }

    fun getBoolean(key: String, defaultValue: Boolean = false): Boolean {
        return prefs.getBoolean(key, defaultValue)
    }

    fun clearAll() {
        prefs.edit().clear().apply()
    }

    fun clearSessionPreservingDevice() {
        val deviceId = getString(KEY_DEVICE_ID)
        prefs.edit().clear().apply()
        if (deviceId != null) saveString(KEY_DEVICE_ID, deviceId)
    }

    companion object {
        const val KEY_SESSION_ID = "key_session_id"
        const val KEY_USER_ID = "key_user_id"
        const val KEY_DEVICE_ID = "key_device_id"
        const val KEY_TRUST_SCORE = "key_trust_score"
        const val KEY_ACCESS_TOKEN = "key_access_token"
        const val KEY_ACCESS_EXPIRES_AT = "key_access_expires_at"
        const val KEY_REFRESH_TOKEN = "key_refresh_token"
        const val KEY_REFRESH_EXPIRES_AT = "key_refresh_expires_at"
        const val KEY_BACKEND_URL = "key_backend_url"
        const val KEY_WS_URL = "key_ws_url"
    }
}
