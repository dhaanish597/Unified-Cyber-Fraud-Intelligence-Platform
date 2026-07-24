plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.hilt.android)
    alias(libs.plugins.ksp)
}

android {
    namespace = "com.fusionbank.mobileapp"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.fusionbank.mobileapp"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }

        buildConfigField("String", "SDK_VERSION", "\"FAT-SDK v2.4.1\"")
        buildConfigField("String", "TENANT_ID", "\"TENANT_FUSB_001\"")
    }

    val releaseStoreFile = providers.gradleProperty("FUSION_RELEASE_STORE_FILE").orNull
    val releaseStorePassword = providers.gradleProperty("FUSION_RELEASE_STORE_PASSWORD").orNull
    val releaseKeyAlias = providers.gradleProperty("FUSION_RELEASE_KEY_ALIAS").orNull
    val releaseKeyPassword = providers.gradleProperty("FUSION_RELEASE_KEY_PASSWORD").orNull
    signingConfigs {
        if (listOf(releaseStoreFile, releaseStorePassword, releaseKeyAlias, releaseKeyPassword).all { !it.isNullOrBlank() }) {
            create("release") {
                storeFile = file(releaseStoreFile!!)
                storePassword = releaseStorePassword
                keyAlias = releaseKeyAlias
                keyPassword = releaseKeyPassword
            }
        }
    }

    buildTypes {
        release {
            buildConfigField("String", "FUSION_BASE_URL", "\"https://fusion.example.invalid/\"")
            buildConfigField("String", "FUSION_WS_URL", "\"wss://fusion.example.invalid/ws/stream\"")
            buildConfigField("String", "FUSION_DEV_CLIENT_ID", "\"\"")
            buildConfigField("String", "FUSION_DEV_CLIENT_SECRET", "\"\"")
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfigs.findByName("release")?.let { signingConfig = it }
        }
        debug {
            buildConfigField("String", "FUSION_BASE_URL", "\"http://10.0.2.2:8001/\"")
            buildConfigField("String", "FUSION_WS_URL", "\"ws://10.0.2.2:8001/ws/stream\"")
            buildConfigField("String", "FUSION_DEV_CLIENT_ID", "\"fusion-android-dev\"")
            buildConfigField("String", "FUSION_DEV_CLIENT_SECRET", "\"fusion-android-local-only\"")
            isMinifyEnabled = false
            applicationIdSuffix = ".debug"
            isDebuggable = true
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
        freeCompilerArgs += listOf(
            "-opt-in=androidx.compose.material3.ExperimentalMaterial3Api",
            "-opt-in=kotlinx.coroutines.ExperimentalCoroutinesApi"
        )
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.8"
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)
    
    // Compose BOM & UI
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    implementation(libs.androidx.material.icons.extended)
    implementation(libs.androidx.navigation.compose)

    // Hilt DI
    implementation(libs.hilt.android)
    ksp(libs.hilt.compiler)
    implementation(libs.androidx.hilt.navigation.compose)

    // Networking
    implementation(libs.retrofit)
    implementation(libs.retrofit.converter.gson)
    implementation(libs.okhttp)
    implementation(libs.okhttp.logging.interceptor)

    // Room DB
    implementation(libs.room.runtime)
    implementation(libs.room.ktx)
    ksp(libs.room.compiler)

    // Security & Coroutines
    implementation(libs.security.crypto)
    implementation("com.google.errorprone:error_prone_annotations:2.26.1")
    implementation(libs.kotlinx.coroutines.android)

    // Debugging / Testing
    debugImplementation(libs.androidx.ui.tooling)
}
