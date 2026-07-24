package com.fusionbank.mobileapp.sdk.network

import com.fusionbank.mobileapp.sdk.models.*
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.POST
import retrofit2.http.Query

interface FusionApiService {
    @POST("device/register")
    suspend fun registerPairedDevice(
        @Body request: PairingRegistrationRequest
    ): Response<PairingRegistrationResponse>

    @POST("banking/auth/login")
    suspend fun bankingLogin(
        @Body request: BankingLoginRequest
    ): Response<BankingAuthResponse>

    @POST("banking/auth/refresh")
    suspend fun refreshBankingToken(
        @Body request: BankingRefreshRequest
    ): Response<BankingAuthResponse>

    @POST("banking/auth/logout")
    suspend fun bankingLogout(
        @Body request: BankingLogoutRequest
    ): Response<Unit>

    @GET("banking/profile")
    suspend fun getBankingProfile(): Response<BankingProfile>

    @POST("auth/token")
    suspend fun createAccessToken(
        @Body request: SDKTokenRequest
    ): Response<SDKTokenResponse>

    @POST("sdk/session/start")
    suspend fun startSession(
        @Body request: SDKSessionStartRequest
    ): Response<SDKSessionResponse>

    @POST("sdk/device")
    suspend fun registerDevice(
        @Body request: SDKDeviceRequest
    ): Response<SDKDeviceResponse>

    @POST("sdk/network")
    suspend fun registerNetwork(
        @Body request: SDKNetworkRequest
    ): Response<SDKNetworkResponse>

    @POST("sdk/event")
    suspend fun reportEvent(
        @Body request: SDKEventRequest
    ): Response<SDKEventResponse>

    @POST("sdk/request-decision")
    suspend fun requestDecision(
        @Body request: SDKDecisionRequest
    ): Response<SDKDecisionResponse>

    @GET("sdk/policies")
    suspend fun getPolicies(): Response<SDKPoliciesResponse>

    @GET("sdk/passport")
    suspend fun getTrustPassport(
        @Query("session_id") sessionId: String
    ): Response<SDKTrustPassportResponse>

    @GET("trust-history/{sessionId}")
    suspend fun getTrustHistory(
        @Path("sessionId") sessionId: String,
        @Query("range") range: String = "last_hour"
    ): Response<SDKTrustHistoryResponse>

    @GET("sdk/health")
    suspend fun getHealth(): Response<SDKHealthResponse>
}
