package com.fusionbank.mobileapp.sdk.queue

import android.util.Log
import com.fusionbank.mobileapp.sdk.models.SDKEventRequest
import com.fusionbank.mobileapp.sdk.network.FusionApiService
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class OfflineEventQueueManager(
    private val eventDao: EventDao,
    private val apiService: FusionApiService
) {
    private val TAG = "OfflineEventQueue"
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    private val _queuedCount = MutableStateFlow(0)
    val queuedCount: StateFlow<Int> = _queuedCount.asStateFlow()

    init {
        updateQueuedCount()
    }

    fun enqueueEvent(request: SDKEventRequest) {
        scope.launch {
            val entity = EventEntity(
                sessionId = request.sessionId,
                deviceId = request.deviceId,
                eventType = request.eventType,
                amount = request.amount
            )
            eventDao.insertEvent(entity)
            updateQueuedCount()
            Log.d(TAG, "Enqueued offline event: ${request.eventType}")
            flushQueue()
        }
    }

    fun flushQueue() {
        scope.launch {
            val pendingEvents = eventDao.getPendingEvents()
            if (pendingEvents.isEmpty()) return@launch

            Log.d(TAG, "Attempting to flush ${pendingEvents.size} queued events...")
            for (event in pendingEvents) {
                try {
                    val req = SDKEventRequest(
                        sessionId = event.sessionId,
                        deviceId = event.deviceId,
                        eventType = event.eventType,
                        amount = event.amount
                    )
                    val response = apiService.reportEvent(req)
                    if (response.isSuccessful) {
                        eventDao.deleteEvent(event.id)
                        Log.d(TAG, "Successfully synced event ID #${event.id}")
                    } else {
                        Log.w(TAG, "Failed sync event #${event.id}: HTTP ${response.code()}")
                        break // Stop processing to maintain chronological ordering
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Network exception while syncing event #${event.id}: ${e.message}")
                    break // Stop retry loop until network recovers
                }
            }
            updateQueuedCount()
        }
    }

    private fun updateQueuedCount() {
        scope.launch {
            _queuedCount.value = eventDao.getPendingCount()
        }
    }
}
