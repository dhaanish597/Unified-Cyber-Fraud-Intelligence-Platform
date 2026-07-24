package com.fusionbank.mobileapp.sdk.queue

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "offline_events")
data class EventEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val sessionId: String,
    val deviceId: String,
    val eventType: String,
    val amount: Double,
    val requestId: String,
    val correlationId: String,
    val timestamp: Long = System.currentTimeMillis(),
    val status: String = "PENDING"
)
