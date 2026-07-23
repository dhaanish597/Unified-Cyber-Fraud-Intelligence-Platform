package com.fusionbank.mobileapp.di

import android.content.Context
import com.fusionbank.mobileapp.sdk.Fusion
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideFusionSdk(): Fusion = Fusion
}
