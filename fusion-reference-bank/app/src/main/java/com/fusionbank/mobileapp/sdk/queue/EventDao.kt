package com.fusionbank.mobileapp.sdk.queue

import androidx.room.*

@Dao
interface EventDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertEvent(event: EventEntity): Long

    @Query("SELECT * FROM offline_events WHERE status = 'PENDING' ORDER BY timestamp ASC")
    suspend fun getPendingEvents(): List<EventEntity>

    @Query("DELETE FROM offline_events WHERE id = :id")
    suspend fun deleteEvent(id: Long)

    @Query("SELECT COUNT(*) FROM offline_events WHERE status = 'PENDING'")
    suspend fun getPendingCount(): Int
}
