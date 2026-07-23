package com.fusionbank.mobileapp.sdk.network

import com.fusionbank.mobileapp.sdk.models.*
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Query

interface FusionApiService {

    @POST("sdk/session/start")
    async suspend fun startSession(
        @Body request: SDKSessionStartRequest
    ): Response<SDKSessionResponse>

    @POST("sdk/device")
    async suspend fun registerDevice(
        @Body request: SDKDeviceRequest
    ): Response<SDKDeviceResponse>

    @POST("sdk/network")
    async suspend fun registerNetwork(
        @Body request: SDKNetworkRequest
    ): Response<SDKNetworkResponse>

    @POST("sdk/event")
    async suspend fun reportEvent(
        @Body request: SDKEventRequest
    ): Response<SDKEventResponse>

    @POST("sdk/request-decision")
    async suspend fun requestDecision(
        @Body request: SDKDecisionRequest
    ): Response<SDKDecisionResponse>

    @GET("sdk/policies")
    async suspend fun getPolicies(): Response<SDKPoliciesResponse>

    @GET("sdk/passport")
    async suspend fun getTrustPassport(
        @Query("session_id") sessionId: String
    ): Response<SDKTrustPassportResponse>

    @GET("sdk/health")
    async suspend fun getHealth(): Response<SDKHealthResponse>
}
