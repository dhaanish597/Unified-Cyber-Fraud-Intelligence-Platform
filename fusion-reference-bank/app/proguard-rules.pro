# Keep Retrofit models
-keepclassmembers class * {
    @com.google.gson.annotations.SerializedName <fields>;
}
-keep class com.fusionbank.mobileapp.sdk.models.** { *; }

# Keep Hilt generated classes
-keep class **_Factory { *; }
-keep class **_MembersInjector { *; }

# Keep OkHttp
-dontwarn okhttp3.**
-dontwarn okio.**

# Keep Room
-keep class * extends androidx.room.RoomDatabase
